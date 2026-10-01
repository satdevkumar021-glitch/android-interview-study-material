# 1A — Kotlin Basics & Null Safety
**One-line summary:** Core Kotlin syntax and the type-system mechanism that eliminates NullPointerExceptions at compile time.
**ID:** 1A | **Priority:** Tier 1

---

## 1. Overview

### What it is
Kotlin's type system distinguishes **nullable** (`T?`) from **non-null** (`T`) types at compile time. Combined with `val`/`var`, type inference, and safe-access operators, it makes null handling explicit and eliminates entire classes of runtime crashes.

### Why it exists
Java's `null` is untyped — any reference can be null, but the compiler never tells you. Kotlin makes nullability part of the type signature, enforced by the compiler. A `String` **cannot** be null; only a `String?` can.

### Problem it solves
- `NullPointerException` (NPE) — the "billion-dollar mistake"
- Verbose, defensive Java null-checks scattered through every layer
- Unclear API contracts ("does this function return null or not?")

---

## 2. How It Works

### `val` vs `var`
```kotlin
val userId: String = "u_123"   // immutable reference — prefer this
var retryCount: Int = 0        // mutable reference — use only when mutation is needed
```
`val` = assign once (like Java `final`). Does **not** mean the object itself is immutable.

### Type Inference
```kotlin
val name = "Alice"          // inferred: String
val scores = listOf(1,2,3)  // inferred: List<Int>
```
The compiler infers the type from the right-hand side. Explicit types only needed for clarity or when inference fails.

### Nullable vs Non-null
```kotlin
var email: String  = "a@b.com"  // non-null — compiler guarantees never null
var phone: String? = null        // nullable — must handle null explicitly
```

### Safe Call `?.`
```kotlin
val length = phone?.length  // returns null instead of throwing NPE
```
Short-circuits the chain if the receiver is null.

### Elvis Operator `?:`
```kotlin
val displayPhone = phone ?: "N/A"       // default if null
val len = phone?.length ?: 0            // safe call + default
throw phone ?: throw IllegalStateException("Phone required")  // throw on null
```

### `let` with Null Handling
```kotlin
phone?.let { p ->
    // p is non-null String inside this block
    sendSms(p)
}
```
Executes the lambda only when the receiver is non-null. Clean alternative to null-check if blocks.

### `!!` (Not-Null Assertion)
```kotlin
val len = phone!!.length  // throws KotlinNullPointerException if phone is null
```
Converts `T?` to `T` at runtime. **Avoid in production code.** Every `!!` is a potential crash that bypasses the compiler's safety net.

### `lateinit`
```kotlin
@Inject lateinit var analytics: AnalyticsService

// later, after Hilt injection:
analytics.track("screen_view")
```
- Used for **non-null** `var` properties that cannot be initialized at declaration time (DI, Android lifecycle).
- Only for reference types (not `Int`, `Boolean`, etc.).
- Throws `UninitializedPropertyAccessException` if accessed before init.
- Check: `::analytics.isInitialized`

### `lazy`
```kotlin
val heavyConfig: Config by lazy {
    Config.load()   // called once, on first access, thread-safe by default
}
```
- Used for **val** properties with expensive initialization.
- Default mode: `LazyThreadSafetyMode.SYNCHRONIZED` — safe for multi-thread.
- Modes: `SYNCHRONIZED`, `PUBLICATION`, `NONE`.
- Not a replacement for `lateinit` — `lazy` requires a `val`.

### ASCII Flow — Null Safety Decision Tree
```
Access property on T?
        |
   is it null?
   /         \
 YES          NO
  |            |
returns       safe
 null /      access
default       value
```

### Key Terms
| Term | Meaning |
|------|---------|
| `val` | Immutable reference |
| `var` | Mutable reference |
| `T?` | Nullable type |
| `?.` | Safe call — returns null if receiver is null |
| `?:` | Elvis — provides default when left is null |
| `!!` | Force-unwrap — throws if null |
| `let` | Scope function — executes block if non-null |
| `lateinit` | Deferred non-null init for `var` |
| `lazy` | Lazy-init delegate for `val` |

---

## 3. Why and When to Use It

### Real Android Use Cases
| Situation | Tool |
|-----------|------|
| ViewModel injected by Hilt | `lateinit var` |
| Expensive singleton (e.g., OkHttpClient) | `by lazy` |
| Optional API field (e.g., `middleName`) | `String?` + `?.` / `?:` |
| Fragment arguments (Bundle) | `?.let { }` |
| Chained nullable calls | `?.` chain |
| Providing default for missing config | `?:` |

### When NOT to Use
- Do **not** use `!!` in production code — extract a non-null guarantee via early-return or `requireNotNull()` instead.
- Do **not** use `lateinit` for `val` properties — use `by lazy`.
- Do **not** use `var` when `val` works — mutable state is harder to reason about in Compose/Flow.
- Do **not** use `lazy` when the property may need re-initialization — `lateinit var` is the right tool there.

---

## 4. How We Use It (Production Example)

**Scenario:** Banking app — user profile screen. Profile fields like middle name are optional from the backend; analytics service is Hilt-injected.

```kotlin
// domain/model/UserProfile.kt
data class UserProfile(
    val userId: String,           // always present
    val fullName: String,
    val middleName: String?,      // optional — backend may omit
    val accountNumber: String,
    val email: String?            // optional until verified
)

// presentation/profile/ProfileViewModel.kt
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() {

    // lateinit: injected, cannot be null, but init happens after constructor
    @Inject lateinit var analytics: AnalyticsService

    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    // lazy: expensive formatter — created once, only if needed
    private val currencyFormatter: NumberFormat by lazy {
        NumberFormat.getCurrencyInstance(Locale("en", "IN"))
    }

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            val result = getUserProfileUseCase(userId)
            result.fold(
                onSuccess = { profile ->
                    // Elvis: display "N/A" if middleName is null
                    val displayName = profile.middleName?.let { middle ->
                        "${profile.fullName} ($middle)"
                    } ?: profile.fullName   // default to fullName if no middle name

                    // Safe call chain: email might be null
                    val maskedEmail = profile.email
                        ?.takeIf { it.contains("@") }
                        ?.replace(Regex("(?<=.).(?=[^@]*@)"), "*")
                        ?: "Not provided"

                    _uiState.value = ProfileUiState.Success(
                        displayName = displayName,
                        maskedEmail = maskedEmail,
                        formattedBalance = currencyFormatter.format(0)
                    )
                },
                onFailure = { _uiState.value = ProfileUiState.Error(it.message ?: "Unknown error") }
            )
        }
    }
}
```

**Key lines:**
- `lateinit var analytics` — Hilt injects this after object construction; non-null guaranteed post-injection.
- `by lazy { ... }` — `NumberFormat` creation is deferred; only paid if `loadProfile` is called.
- `?.let { middle -> ... } ?: profile.fullName` — reads clearly: "if middle name exists, include it; otherwise use full name."
- `?.takeIf { }?.replace(...)` — safe call chain; short-circuits to null at any null point, then `?:` provides the fallback.
- No `!!` anywhere — the compiler-enforced contract holds throughout.

---

## 5. Alternatives and Trade-offs

| Approach | Pros | Cons | When to pick |
|----------|------|------|--------------|
| Kotlin nullable `T?` + operators | Compile-time safety, idiomatic, concise | Requires nullable discipline across layers | Always — default choice |
| `!!` (force-unwrap) | One less null-check | Runtime crash if null; bypasses safety | Never in prod; only in tests when you own the invariant |
| `lateinit var` | Clean DI / lifecycle init | Crash if accessed before init; only reference types | Non-null var that can't be init'd at declaration (DI, lifecycle) |
| `by lazy` | Thread-safe, one-time init, val | Can't re-init; slight overhead on first access | Expensive val init deferred to first use |
| `Optional<T>` (Java) | Familiar to Java devs | Verbose, heap allocation per wrap, not idiomatic Kotlin | Never — use `T?` |
| Sentinel value (e.g. `""`, `-1`) | No nullability | Implicit contract, error-prone | Never — use `T?` |

**Interviewer comparisons:**
- `lateinit` vs `by lazy`: mutable/deferred vs immutable/computed-once.
- `?.` vs `!!`: safe vs force — always prefer safe.
- `val` vs `var`: immutability preference in functional/reactive code.

---

## 6. Pitfalls and Best Practices

### Common Mistakes

**Bad: `!!` in production**
```kotlin
// BAD — crashes if userData is null
val name = userData!!.name
```
```kotlin
// GOOD — explicit contract
val name = userData?.name ?: return  // early exit
// or
val name = requireNotNull(userData) { "userData must not be null here" }.name
```

**Bad: `lateinit` for primitives**
```kotlin
// BAD — won't compile: lateinit not allowed on Int
lateinit var count: Int
```
```kotlin
// GOOD
var count: Int = 0
```

**Bad: ignoring `isInitialized`**
```kotlin
// BAD — throws UninitializedPropertyAccessException
fun track() = analytics.track("event")  // analytics may not be initialized yet
```
```kotlin
// GOOD
fun track() {
    if (::analytics.isInitialized) analytics.track("event")
}
```

**Bad: mutable state for Compose / Flow**
```kotlin
// BAD — var breaks unidirectional data flow
var userName: String = ""
```
```kotlin
// GOOD — val + StateFlow / MutableState
val userName: StateFlow<String> = _userName.asStateFlow()
```

**Bad: `lazy` on a mutable value that changes**
```kotlin
// BAD — lazy cached the first value; updates not reflected
val token: String by lazy { prefs.getToken() }
```
```kotlin
// GOOD — token changes; use a function or StateFlow
fun getToken(): String = prefs.getToken()
```

### Memory / Threading / Lifecycle
- `lateinit` is **not thread-safe** — avoid concurrent access without synchronization.
- `by lazy` default (`SYNCHRONIZED`) uses a lock; choose `NONE` only in single-threaded contexts for performance.
- Safe calls in Compose lambdas: Kotlin's smart cast can fail inside lambdas — use `val local = nullable; local?.use()` pattern.

### Production Best Practices
1. Prefer `val` over `var` everywhere possible.
2. Prefer `T?` with `?.` / `?:` over `!!`.
3. Use `requireNotNull()` / `checkNotNull()` to document invariants with a meaningful message.
4. Model optional API fields as `T?` in your domain model — never use sentinel values.
5. Use `by lazy` for expensive one-time initializations (parsers, formatters, heavy config).
6. Use `lateinit` only for DI / lifecycle-bound non-null properties; always check `isInitialized` if there's any doubt.

---

## 7. Interview Answer Framework

### 30-Second Answer
> "Kotlin's null safety makes nullability part of the type system. A plain `String` can never be null — only `String?` can. The compiler forces you to handle the null case via safe calls `?.`, the Elvis operator `?:`, or smart casts. This eliminates NPEs at compile time rather than at runtime. For deferred init, `lateinit` handles DI/lifecycle-bound vars, and `by lazy` handles expensive val computations that should run once."

### 2-Minute Structured Answer
> "The core idea is that nullability is a compile-time type distinction, not a runtime surprise. `String` and `String?` are different types. The compiler refuses to let you call methods on a `String?` without first handling the null case.
>
> In practice, I use `?.` for safe chaining — the whole chain short-circuits to null if any receiver is null. `?:` provides a default or triggers an early return. `let` executes a block only when the receiver is non-null, which is cleaner than an `if (x != null)` block when you need a scoped non-null reference.
>
> `!!` exists but I treat it as a code smell. Every `!!` means 'I'm overriding the compiler — crash if I'm wrong.' In production I replace it with `requireNotNull()` with a message, or restructure the code so the null case is impossible at the call site.
>
> For property initialization: `lateinit var` is for Hilt-injected or lifecycle-driven non-null properties that can't be set in the constructor. `by lazy` is for expensive `val` computations deferred to first access — thread-safe by default. They're complementary, not interchangeable — `lazy` requires `val`, `lateinit` requires `var`."

### Must-Mention Points
1. `T` vs `T?` — compile-time distinction, not a runtime wrapper.
2. `?.` short-circuits the entire chain to null on the first null receiver.
3. `?:` — Elvis provides a default **or** throws/returns; right side executes lazily.
4. `!!` is a deliberate override of compile-time safety — production code should not contain it.
5. `lateinit` — `var`, reference types only, crashes with `UninitializedPropertyAccessException` (not NPE).
6. `by lazy` — `val`, computed once, `SYNCHRONIZED` by default.
7. Smart casts: after `if (x != null)`, Kotlin promotes `x` to non-null inside the block.
8. `requireNotNull()` / `checkNotNull()` — preferred over `!!` when you must assert non-null with context.

### Do Not Go Deeper Unless Asked
- Kotlin's compilation to JVM bytecode representation of nullable types (platform types, `@Nullable`/`@NotNull` annotations).
- `LazyThreadSafetyMode.PUBLICATION` vs `NONE` internals.
- Delegation internals for `by lazy`.

### Likely Follow-up Questions

**Q: What is a platform type?**
> A type from Java that Kotlin cannot determine is null or non-null (displayed as `String!`). Kotlin trusts you — it becomes your responsibility. Annotate Java APIs with `@Nullable`/`@NotNull` to fix this.

**Q: Difference between `val` and `const val`?**
> `val` is a runtime immutable reference. `const val` is a compile-time constant — only for primitives and `String`, inlined at usage sites. Used for constants in `companion object` or top-level.

**Q: When does smart cast fail?**
> Smart cast fails when the compiler can't guarantee the value hasn't changed between the check and the use — e.g., a `var` property (another thread could change it) or a `val` property in another class (another getter could return different values).

**Q: `let` vs `also` for null checks?**
> Use `let` when you need the non-null value transformed or used inside the block. Use `also` when you need a side effect but still return the original receiver.

### Senior-Level Insight
> "In a multi-module Clean Architecture, nullable types in your domain model act as a formal API contract between modules. If `UserProfile.email` is `String?`, every consumer — presentation, domain, data — must handle the missing case explicitly. This is far more robust than a convention like 'check the docs' or a sentinel value. I enforce a rule: domain models never use `!!`, and any conversion from data layer DTO to domain model must resolve nullability explicitly in the mapper."

---

## 8. Quick Revision Sheet

```
VAL vs VAR
  val  = assign once (immutable ref) — PREFER
  var  = mutable reference — use sparingly

NULLABLE TYPES
  String   — can NEVER be null (compiler enforces)
  String?  — can be null (must handle explicitly)

SAFE OPERATORS
  ?.       — safe call; short-circuits to null if receiver is null
  ?:       — Elvis; provides default / throws / returns if left is null
  !!       — force-unwrap; throws KotlinNullPointerException if null — AVOID
  ?.let{}  — execute block only if non-null, scoped non-null reference

SMART CAST
  if (x != null) { x.doSomething() }  — compiler promotes x to non-null

PREFER OVER !!
  requireNotNull(x) { "message" }
  checkNotNull(x)   { "message" }
  x ?: return / throw ...

LATEINIT
  - var only, reference types only
  - crashes: UninitializedPropertyAccessException (not NPE)
  - check: ::prop.isInitialized
  - use for: DI injection, lifecycle-bound init

BY LAZY
  - val only
  - computed once on first access
  - default: LazyThreadSafetyMode.SYNCHRONIZED (thread-safe)
  - use for: expensive one-time computations

KEY GOTCHAS
  - Smart cast fails on var properties and mutable class members
  - lateinit is NOT thread-safe
  - by lazy with NONE mode is not thread-safe — only use in single-threaded context
  - Platform types (T!) from Java — annotate Java side to fix
  - !! in tests: acceptable; in production: code smell
```

---

## 9. Interview Questions (Self-Check)

### Basic
**B1** *(Easy)* — What is the difference between `val` and `var` in Kotlin?

**B2** *(Easy)* — What is the difference between `String` and `String?` in Kotlin? How does the compiler enforce it?

**B3** *(Easy)* — What does the Elvis operator `?:` do? Give an example.

### Intermediate
**I1** *(Medium)* — When would you use `lateinit var` vs `by lazy`? What happens if you access a `lateinit` property before it is initialized?

**I2** *(Medium)* — Why should you avoid `!!` in production code? What are the better alternatives?

**I3** *(Medium)* — Explain smart casts. When does a smart cast fail?

**I4** *(Medium — Coding)* — Rewrite the following without any `!!`:
```kotlin
fun getDisplayName(user: User?): String {
    return user!!.profile!!.displayName!!
}
```

### Senior / Scenario
**S1** *(Hard — Scenario)* — Your teammate wrote this in a ViewModel:
```kotlin
var userSession: UserSession? = null

fun loadDashboard() {
    viewModelScope.launch {
        userSession = repository.getSession()
        dashboard.load(userSession!!.token)
    }
}
```
What are the problems? How do you fix it?

**S2** *(Hard)* — In a multi-module app, the `:data` module returns `UserDto` with `email: String?`. The `:domain` module's `UserProfile` has `email: String?` too. A junior dev maps them with `userProfile.email = dto.email!!`. What's wrong, and how do you enforce the right pattern?

**S3** *(Hard — Scenario)* — `by lazy` is used to initialize an OkHttpClient in a Repository. The app crashes in production with a `ConcurrentModificationException` inside the lazy initializer. Why? How do you fix it?

---

## Answer Key

**B1:** `val` is an immutable reference — assigned once, cannot be reassigned. `var` is mutable — can be reassigned. Neither controls whether the object itself is mutable.

**B2:** `String` is a non-null type; the compiler guarantees it will never hold null and won't compile code that could assign null to it. `String?` is nullable; the compiler forces you to handle the null case (via `?.`, `?:`, or null check) before calling any method on it.

**B3:** The Elvis operator returns the left-hand expression if it is non-null, or the right-hand expression if it is null. Example: `val name = user?.name ?: "Guest"` — if `user` is null or `user.name` is null, name becomes `"Guest"`.

**I1:** `lateinit var` — for non-null `var` properties that cannot be initialized at declaration time (DI, lifecycle callbacks). Only reference types. Throws `UninitializedPropertyAccessException` if accessed before init. `by lazy` — for non-null `val` properties with an expensive computation that should run once and be cached. If `lateinit` is accessed before init: `UninitializedPropertyAccessException`.

**I2:** `!!` bypasses the compiler's null safety — it will throw `KotlinNullPointerException` at runtime if the value is null, defeating the purpose of the type system. Better alternatives: `requireNotNull(x) { "descriptive message" }`, `x ?: return`, `x ?: throw IllegalStateException("x must not be null")`, or restructuring the code so the null case is impossible at the call site.

**I3:** Smart cast is when the compiler automatically promotes a nullable type to non-null after a null check (or `is` check). It fails when the compiler can't guarantee the value hasn't changed: (1) `var` properties — another thread could reassign them between the check and the use; (2) mutable class members — a custom getter could return a different value each time.

**I4:**
```kotlin
fun getDisplayName(user: User?): String {
    val profile = user?.profile ?: return "Unknown"
    return profile.displayName ?: "Unknown"
}
// or concisely:
fun getDisplayName(user: User?): String =
    user?.profile?.displayName ?: "Unknown"
```

**S1:** Problems: (1) `userSession` is a `var` — the smart cast after `= repository.getSession()` is unsafe because another coroutine could set it to null between the assignment and `userSession!!.token`. (2) `!!` will crash if `getSession()` returns null. Fix:
```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        val session = repository.getSession() ?: run {
            _uiState.value = UiState.Error("No session")
            return@launch
        }
        dashboard.load(session.token)  // session is non-null here
    }
}
```
Use a local `val` to capture the result — the compiler can smart-cast a local `val`, not a `var` field.

**S2:** The `!!` in the mapper means: "I assert this email is never null coming from the DTO." That's a contract violation — the DTO declares it as nullable for a reason. If the backend ever omits the email, production crashes. Fix: make the mapper explicit:
```kotlin
// mapper in :data module
fun UserDto.toDomain() = UserProfile(
    email = email  // nullable String? maps to nullable String? — honest
)
```
If domain requires non-null email, add validation/business logic in the UseCase, not the mapper.

**S3:** `by lazy` default mode is `SYNCHRONIZED` — it uses a lock to ensure single initialization. `ConcurrentModificationException` in the initializer likely means the initializer itself is modifying a collection (or OkHttpClient internal state) that is being iterated, not a threading issue with `lazy` itself. The fix is to ensure the initializer lambda is free of concurrent collection modification. If you changed the mode to `NONE` for performance, then yes — two threads could enter the initializer simultaneously; revert to `SYNCHRONIZED` or `PUBLICATION`.
