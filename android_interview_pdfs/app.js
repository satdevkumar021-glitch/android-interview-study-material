/**
 * Android Interview Study Material — App Logic
 * Handles: navigation, progress tracking, quiz scoring, search, PDF download
 */

// ─── Syllabus Data ───────────────────────────────────────────────────────────
const SYLLABUS = [
  {
    section: "1 · Kotlin",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "1A", name: "Basics & Null Safety", file: "1A_Kotlin_Basics_Null_Safety.html", tags: ["val/var","nullable","Elvis","lateinit","lazy"] },
      { id: "1B", name: "Functions", file: "1B_Kotlin_Functions.html", tags: ["extension","lambda","HOF","SAM"] },
      { id: "1C", name: "Scope Functions", file: "1C_Scope_Functions.html", tags: ["let","run","with","apply","also"] },
      { id: "1D", name: "OOP", file: "1D_Kotlin_OOP.html", tags: ["class","inheritance","interface","abstract"] },
      { id: "1E", name: "Special Classes", file: "1E_Special_Classes.html", tags: ["data","enum","sealed","object","companion"] },
      { id: "1F", name: "Generics & Variance", file: "1F_Generics_Variance.html", tags: ["generics","in","out","covariance"] },
      { id: "1G", name: "Delegation & Operators", file: "1G_Delegation_Operators.html", tags: ["delegation","lazy","operator","destructuring"] },
      { id: "1H", name: "Collections", file: "1H_Collections.html", tags: ["List","Map","filter","fold","Sequence"] },
      { id: "1I", name: "Inline & Recursion", file: "1I_Inline_Recursion.html", tags: ["inline","noinline","crossinline","reified","tailrec"] },
      { id: "1J", name: "Equality, Interop & Errors", file: "1J_Equality_Interop_Errors.html", tags: ["==","===","Result","exceptions","JVM interop"] },
    ]
  },
  {
    section: "2 · Android Fundamentals",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "2A", name: "Components Overview", file: "2A_Components_Overview.html", tags: ["Activity","Fragment","Service","BroadcastReceiver","ContentProvider","Context"] },
      { id: "2B", name: "Activity Lifecycle & State", file: "2B_Activity_Lifecycle_State.html", tags: ["onCreate","onPause","rotation","process death","SavedStateHandle"] },
      { id: "2C", name: "Launch Modes & Back Stack", file: "2C_Launch_Modes_Back_Stack.html", tags: ["singleTop","singleTask","FLAG_ACTIVITY_CLEAR_TASK","back stack"] },
      { id: "2D", name: "Fragments", file: "2D_Fragments.html", tags: ["viewLifecycleOwner","ViewBinding","activityViewModels","Fragment Result"] },
      { id: "2E", name: "Intents", file: "2E_Intents.html", tags: ["explicit","implicit","PendingIntent","deep link","App Link"] },
    ]
  },
  {
    section: "3 · Framework Internals",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "3A", name: "App Startup", file: "3A_App_Startup.html", tags: ["Zygote","ActivityManagerService","ActivityThread","cold start"] },
      { id: "3B", name: "Main Thread Internals", file: "3B_Main_Thread_Internals.html", tags: ["Looper","MessageQueue","Handler","main thread"] },
      { id: "3C", name: "Binder & IPC", file: "3C_Binder_IPC.html", tags: ["Binder","IPC","AIDL","IBinder"] },
      { id: "3D", name: "Process Model", file: "3D_Process_Model.html", tags: ["process priority","UID","sandbox","ANR","OOM killer"] },
    ]
  },
  {
    section: "4 · Jetpack Components",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "4A", name: "ViewModel", file: "4A_ViewModel.html", tags: ["ViewModelStore","viewModelScope","SavedStateHandle","shared ViewModel"] },
      { id: "4B", name: "LiveData", file: "4B_LiveData.html", tags: ["lifecycle-aware","setValue","postValue","MediatorLiveData"] },
      { id: "4C", name: "Lifecycle", file: "4C_Lifecycle.html", tags: ["LifecycleOwner","repeatOnLifecycle","lifecycleScope","DefaultLifecycleObserver"] },
    ]
  },
  {
    section: "5 · Kotlin Coroutines",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "5A", name: "Fundamentals", file: "5A_Coroutines_Fundamentals.html", tags: ["coroutine","CoroutineScope","CoroutineContext","Job","Dispatcher"] },
      { id: "5B", name: "Builders & Dispatchers", file: "5B_Builders_Dispatchers.html", tags: ["launch","async","withContext","Dispatchers.IO","Dispatchers.Main"] },
      { id: "5C", name: "Structured Concurrency", file: "5C_Structured_Concurrency.html", tags: ["coroutineScope","supervisorScope","Job","SupervisorJob","structured concurrency"] },
      { id: "5D", name: "Cancellation & Exceptions", file: "5D_Cancellation_Exceptions.html", tags: ["cancellation","CancellationException","CoroutineExceptionHandler","NonCancellable"] },
      { id: "5E", name: "Scopes, Concurrency & Testing", file: "5E_Scopes_Concurrency_Testing.html", tags: ["viewModelScope","Mutex","Semaphore","runTest","TestDispatcher"] },
    ]
  },
  {
    section: "6 · Kotlin Flow",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "6A", name: "Flow Core", file: "6A_Flow_Core.html", tags: ["cold flow","StateFlow","SharedFlow","hot flow","collect"] },
      { id: "6B", name: "Flow Operators", file: "6B_Flow_Operators.html", tags: ["map","flatMapLatest","combine","debounce","catch","retry"] },
      { id: "6C", name: "Builders & Channels", file: "6C_Builders_Channels.html", tags: ["callbackFlow","channelFlow","Channel","backpressure","conflate"] },
      { id: "6D", name: "Sharing", file: "6D_Sharing.html", tags: ["stateIn","shareIn","SharingStarted","WhileSubscribed"] },
    ]
  },
  {
    section: "7 · Jetpack Compose",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "7A", name: "Fundamentals", file: "7A_Compose_Fundamentals.html", tags: ["@Composable","recomposition","composition","slot table","State"] },
      { id: "7B", name: "State Management", file: "7B_State_Management.html", tags: ["remember","rememberSaveable","state hoisting","UDF","collectAsStateWithLifecycle"] },
      { id: "7C", name: "Side Effects", file: "7C_Side_Effects.html", tags: ["LaunchedEffect","DisposableEffect","SideEffect","snapshotFlow","produceState"] },
      { id: "7D", name: "Performance", file: "7D_Compose_Performance.html", tags: ["stability","@Stable","@Immutable","skippable","LazyColumn keys","compiler metrics"] },
      { id: "7E", name: "Compose UI", file: "7E_Compose_UI.html", tags: ["Row","Column","Box","LazyColumn","Scaffold","Modifier","Material 3"] },
      { id: "7F", name: "Navigation", file: "7F_Compose_Navigation.html", tags: ["NavController","NavHost","type-safe routes","nested nav","deep links"] },
    ]
  },
  {
    section: "8 · Architecture",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "8A", name: "Architecture Patterns", file: "8A_Architecture_Patterns.html", tags: ["MVC","MVP","MVVM","MVI","UDF"] },
      { id: "8B", name: "Clean Architecture", file: "8B_Clean_Architecture.html", tags: ["Presentation","Domain","Data","UseCase","Repository","Mapper"] },
    ]
  },
  {
    section: "9 · SOLID",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "9A", name: "SOLID Principles", file: "9A_SOLID_Principles.html", tags: ["SRP","OCP","LSP","ISP","DIP","Android examples"] },
    ]
  },
  {
    section: "10 · Design Patterns",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "10A", name: "Creational Patterns", file: "10A_Creational_Patterns.html", tags: ["Singleton","Factory","Builder","Abstract Factory"] },
      { id: "10B", name: "Structural Patterns", file: "10B_Structural_Patterns.html", tags: ["Adapter","Decorator","Facade","Proxy"] },
      { id: "10C", name: "Behavioral Patterns", file: "10C_Behavioral_Patterns.html", tags: ["Observer","Strategy","Command","State"] },
    ]
  },
  {
    section: "11 · Dependency Injection",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "11A", name: "DI & Hilt Basics", file: "11A_DI_Hilt_Basics.html", tags: ["@Inject","@Provides","@Binds","@Module","@Singleton","qualifiers"] },
      { id: "11B", name: "Hilt Components", file: "11B_Hilt_Components.html", tags: ["SingletonComponent","ViewModelComponent","Dagger codegen","SubComponent"] },
    ]
  },
  {
    section: "12 · Networking",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "12A", name: "REST & HTTP", file: "12A_REST_HTTP.html", tags: ["HTTP verbs","status codes","headers","auth","caching","pagination"] },
      { id: "12B", name: "Retrofit & OkHttp", file: "12B_Retrofit_OkHttp.html", tags: ["Retrofit","OkHttp","interceptors","Moshi","converters"] },
      { id: "12C", name: "Advanced Networking", file: "12C_Advanced_Networking.html", tags: ["certificate pinning","token refresh","Mutex","offline-first","NetworkSecurityConfig"] },
    ]
  },
  {
    section: "13 · Room & Storage",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "13A", name: "Room", file: "13A_Room.html", tags: ["@Entity","@Dao","@Database","TypeConverter","migration","Flow"] },
      { id: "13B", name: "Room vs SQLite", file: "13B_Room_vs_SQLite.html", tags: ["compile-time query","@RawQuery","migration DSL"] },
      { id: "13C", name: "Other Storage", file: "13C_Other_Storage.html", tags: ["DataStore","Proto DataStore","Keystore","EncryptedSharedPreferences"] },
    ]
  },
  {
    section: "14 · Background Processing",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "14A", name: "WorkManager", file: "14A_WorkManager.html", tags: ["CoroutineWorker","constraints","chaining","UniqueWork","retry"] },
      { id: "14B", name: "Choosing the Right Tool", file: "14B_Choosing_Right_Tool.html", tags: ["WorkManager vs Service","AlarmManager","Doze","foreground service"] },
    ]
  },
  {
    section: "15 · Services",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "15A", name: "Services", file: "15A_Services.html", tags: ["started service","bound service","foreground service","LifecycleService","background restrictions"] },
    ]
  },
  {
    section: "16 · BroadcastReceiver",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "16A", name: "BroadcastReceiver", file: "16A_BroadcastReceiver.html", tags: ["static receiver","dynamic receiver","ordered broadcast","goAsync","API 26 restrictions"] },
    ]
  },
  {
    section: "17 · ContentProvider",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "17A", name: "ContentProvider", file: "17A_ContentProvider.html", tags: ["ContentResolver","URI","Cursor","FileProvider","permissions"] },
    ]
  },
  {
    section: "18 · Navigation",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "18A", name: "Navigation & Deep Linking", file: "18A_Navigation.html", tags: ["NavGraph","Safe Args","App Links","popUpTo","nested graph"] },
    ]
  },
  {
    section: "19 · Security",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "19A", name: "Data & Network Security", file: "19A_Data_Network_Security.html", tags: ["Keystore","EncryptedSharedPreferences","certificate pinning","NetworkSecurityConfig","token storage"] },
      { id: "19B", name: "App Hardening & Auth", file: "19B_App_Hardening.html", tags: ["BiometricPrompt","Play Integrity","R8","ProGuard","OWASP MASVS"] },
    ]
  },
  {
    section: "20 · Testing",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "20A", name: "Unit Testing", file: "20A_Unit_Testing.html", tags: ["JUnit","MockK","Fake vs Mock","ViewModel testing","testing pyramid"] },
      { id: "20B", name: "Coroutines & Flow Testing", file: "20B_Coroutines_Flow_Testing.html", tags: ["runTest","StandardTestDispatcher","Turbine","advanceUntilIdle"] },
      { id: "20C", name: "UI & Network Testing", file: "20C_UI_Network_Testing.html", tags: ["Espresso","Compose UI testing","MockWebServer","UI Automator"] },
    ]
  },
  {
    section: "21 · Performance",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "21A", name: "Performance", file: "21A_Performance.html", tags: ["ANR","cold start","Baseline Profiles","Macrobenchmark","StrictMode","jank"] },
    ]
  },
  {
    section: "22 · Memory Management",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "22A", name: "Memory Management", file: "22A_Memory_Management.html", tags: ["heap","GC","WeakReference","memory leak","LeakCanary","Handler leak"] },
    ]
  },
  {
    section: "23 · Gradle",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "23A", name: "Gradle / Build System", file: "23A_Gradle.html", tags: ["AGP","build variants","KSP","KAPT","Version Catalog","build cache"] },
    ]
  },
  {
    section: "24 · Modularization",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "24A", name: "Modularization", file: "24A_Modularization.html", tags: ["feature modules","api vs implementation","Dynamic Feature Modules","build performance"] },
    ]
  },
  {
    section: "25 · CI/CD",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "25A", name: "CI/CD", file: "25A_CICD.html", tags: ["GitHub Actions","Fastlane","Play Store","AAB signing","branching strategy"] },
    ]
  },
  {
    section: "26 · Code Quality",
    tier: 2,
    color: "#56cfb2",
    topics: [
      { id: "26A", name: "Code Quality", file: "26A_Code_Quality.html", tags: ["Android Lint","Detekt","Ktlint","SonarQube","JaCoCo"] },
    ]
  },
  {
    section: "27 · Permissions",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "27A", name: "Permissions", file: "27A_Permissions.html", tags: ["runtime permissions","POST_NOTIFICATIONS","one-time permissions","background location"] },
    ]
  },
  {
    section: "28 · RecyclerView & UI",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "28A", name: "RecyclerView", file: "28A_RecyclerView.html", tags: ["ListAdapter","DiffUtil","ViewHolder","LayoutManager"] },
      { id: "28B", name: "Legacy UI", file: "28B_Legacy_UI.html", tags: ["ViewBinding","DataBinding","ConstraintLayout","custom views"] },
    ]
  },
  {
    section: "29 · Paging",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "29A", name: "Paging 3", file: "29A_Paging3.html", tags: ["PagingSource","RemoteMediator","Pager","LazyPagingItems","cursor pagination"] },
    ]
  },
  {
    section: "30 · System Design",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "30A", name: "Offline-first Product Catalog", file: "30A_System_Design_Offline_Catalog.html", tags: ["Room SSOT","RemoteMediator","stale-while-revalidate","offline-first"] },
      { id: "30B", name: "Login / Auth System", file: "30B_System_Design_Login_Auth.html", tags: ["JWT","token refresh","biometric","Keystore","session"] },
      { id: "30C", name: "Shopping Cart", file: "30C_System_Design_Shopping_Cart.html", tags: ["optimistic updates","conflict resolution","guest cart","sync"] },
      { id: "30D", name: "Chat Application", file: "30D_System_Design_Chat.html", tags: ["WebSocket","offline queue","message states","FCM","pagination"] },
      { id: "30E", name: "Push Notification System", file: "30E_System_Design_Push_Notifications.html", tags: ["FCM","token lifecycle","NotificationChannels","deep links","data vs notification"] },
      { id: "30F", name: "Image-heavy Feed", file: "30F_System_Design_Image_Feed.html", tags: ["Coil","three-level cache","cursor pagination","60fps","Paging 3"] },
      { id: "30G", name: "Large-scale Modular App", file: "30G_System_Design_Large_Scale_App.html", tags: ["millions of users","feature flags","A/B testing","BFF","CI/CD at scale"] },
    ]
  },
  {
    section: "31 · Firebase",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "31A", name: "Firebase", file: "31A_Firebase.html", tags: ["Firestore","FCM","Crashlytics","Remote Config","Analytics","Auth"] },
    ]
  },
  {
    section: "32 · App Release",
    tier: 3,
    color: "#f0a04b",
    topics: [
      { id: "32A", name: "App Release", file: "32A_App_Release.html", tags: ["APK vs AAB","R8","ProGuard","keystore","Play Console","staged rollout"] },
    ]
  },
  {
    section: "33 · Scenario Questions",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "33A", name: "Debugging Scenarios", file: "33A_Debugging_Scenarios.html", tags: ["API called twice","Compose recompose","prod crash","slow startup","Flow leak","Activity leak"] },
      { id: "33B", name: "Data & Concurrency Scenarios", file: "33B_Data_Concurrency_Scenarios.html", tags: ["parallel APIs","sequential APIs","token refresh Mutex","stale cache","10K items"] },
      { id: "33C", name: "Platform & Scale Scenarios", file: "33C_Platform_Scale_Scenarios.html", tags: ["Android 15/16","background restrictions","millions of users","architecture"] },
    ]
  },
  {
    section: "34 · Coding Questions",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "34A", name: "Strings", file: "34A_Strings_Coding.html", tags: ["reverse","palindrome","anagram","character frequency","non-repeating"] },
      { id: "34B", name: "Arrays & Collections", file: "34B_Arrays_Collections_Coding.html", tags: ["Two Sum","remove duplicates","groupBy","Kadane","HashMap"] },
      { id: "34C", name: "Math & Recursion", file: "34C_Math_Recursion_Coding.html", tags: ["Fibonacci","factorial","prime","Sieve","tailrec"] },
      { id: "34D", name: "Data Structures & Search", file: "34D_Data_Structures_Search.html", tags: ["Stack","Queue","LinkedList","Floyd's cycle","binary search"] },
      { id: "34E", name: "Android Coding", file: "34E_Android_Coding.html", tags: ["parallel coroutines","Flow search","LRU cache","token refresh interceptor"] },
    ]
  },
  {
    section: "35 · Behavioral",
    tier: 1,
    color: "#f06b6b",
    topics: [
      { id: "35A", name: "Behavioral & Senior Leadership", file: "35A_Behavioral_Senior_Leadership.html", tags: ["STAR","production bug","architecture decision","mentoring","technical debt"] },
    ]
  },
];

// ─── Progress Store ───────────────────────────────────────────────────────────
const PROGRESS_KEY = "android_study_progress";

function loadProgress() {
  try { return JSON.parse(localStorage.getItem(PROGRESS_KEY) || "{}"); }
  catch { return {}; }
}

function saveProgress(data) {
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(data));
}

function getTopicProgress(topicId) {
  const p = loadProgress();
  return p[topicId] || { status: "not_started", quizScore: null, timeSpent: 0, lastVisited: null };
}

function setTopicProgress(topicId, updates) {
  const p = loadProgress();
  p[topicId] = { ...getTopicProgress(topicId), ...updates };
  saveProgress(p);
}

function getOverallStats() {
  const p = loadProgress();
  const total = SYLLABUS.reduce((sum, s) => sum + s.topics.length, 0);
  const started = Object.values(p).filter(t => t.status !== "not_started").length;
  const completed = Object.values(p).filter(t => t.status === "completed").length;
  const scores = Object.values(p).filter(t => t.quizScore !== null).map(t => t.quizScore);
  const avgScore = scores.length ? Math.round(scores.reduce((a,b)=>a+b,0)/scores.length) : 0;
  return { total, started, completed, avgScore };
}

// ─── Exports ─────────────────────────────────────────────────────────────────
window.APP = { SYLLABUS, getTopicProgress, setTopicProgress, getOverallStats, loadProgress };
