import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { z } from "zod";
import {
  Archive,
  ArrowDownToLine,
  ArrowLeftRight,
  BarChart3,
  Building2,
  Bell,
  BookOpen,
  Boxes,
  ChevronDown,
  CircleDollarSign,
  CircleHelp,
  ClipboardList,
  CreditCard,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Package,
  Palette,
  Plus,
  ReceiptText,
  Search,
  Settings,
  ShoppingCart,
  SlidersHorizontal,
  Sparkles,
  Store,
  Tag,
  Trash2,
  TrendingUp,
  UserRound,
  UserPlus,
  UsersRound,
  X,
  Check,
  RefreshCw,
} from "lucide-react";
import {
  authApi,
  categoriesApi,
  customersApi,
  inventoryApi,
  paymentsApi,
  productsApi,
  receiptsApi,
  reportsApi,
  returnsApi,
  salesApi,
} from "./api/client";

const cashierId = import.meta.env.VITE_CASHIER_ID || "";
const cashierLabel = import.meta.env.VITE_CASHIER_NAME || "Configured cashier";
const getActiveCashierId = () => {
  try {
    return (
      JSON.parse(localStorage.getItem("bookstore-account") || "null")?.id ||
      cashierId
    );
  } catch {
    return cashierId;
  }
};
const money = (value) => `K${Number(value || 0).toFixed(2)}`;
const initials = (name) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, roles: ["OWNER", "ADMIN", "MANAGER", "CASHIER", "INVENTORY_MANAGER"] },
  { to: "/pos", label: "Point of sale", icon: ShoppingCart, roles: ["OWNER", "ADMIN", "MANAGER", "CASHIER"] },
  { to: "/sales", label: "Sales history", icon: ReceiptText, roles: ["OWNER", "ADMIN", "MANAGER", "CASHIER"] },
  { to: "/returns", label: "Returns", icon: ArrowLeftRight, roles: ["OWNER", "ADMIN", "MANAGER", "CASHIER"] },
  { to: "/products", label: "Products", icon: BookOpen, roles: ["OWNER", "ADMIN", "MANAGER", "INVENTORY_MANAGER"] },
  { to: "/inventory", label: "Inventory", icon: Boxes, roles: ["OWNER", "ADMIN", "MANAGER", "INVENTORY_MANAGER"] },
  { to: "/customers", label: "Customers", icon: UsersRound, roles: ["OWNER", "ADMIN", "MANAGER", "CASHIER"] },
  { to: "/reports", label: "Reports", icon: BarChart3, roles: ["OWNER", "ADMIN", "MANAGER", "INVENTORY_MANAGER"] },
];

function App() {
  const navigate = useNavigate();
  const [account, setAccount] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("bookstore-account") || "null");
    } catch {
      return null;
    }
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [role, setRole] = useState(
    localStorage.getItem("pos-role") || "Cashier",
  );
  const [toast, setToast] = useState(null);
  const location = useLocation();
  const queryClient = useQueryClient();
  const [selectedBranchId, setSelectedBranchId] = useState(
    () => localStorage.getItem("bookstore-branch-id") || account?.branch || "",
  );
  const clientConfig = useQuery({
    queryKey: ["client-config"],
    queryFn: authApi.client,
    enabled: Boolean(account),
  });
  const configuredClient = clientConfig.data;
  const availableBranches = configuredClient?.branches || [];
  const configuredBranch = availableBranches.find((branch) => branch.id === selectedBranchId) || availableBranches[0];
  const accountRole = (account?.role_name || role || "CASHIER").toUpperCase();
  const normalizedRole = accountRole.includes("CASHIER") ? "CASHIER" : accountRole;
  const visibleNavItems = navItems.filter(({ roles }) => roles.includes(normalizedRole));

  useEffect(() => {
    if (!selectedBranchId && configuredBranch?.id) {
      setSelectedBranchId(configuredBranch.id);
      localStorage.setItem("bookstore-branch-id", configuredBranch.id);
    }
  }, [selectedBranchId, configuredBranch]);

  const canSwitchBranches = ["OWNER", "ADMIN", "MANAGER", "INVENTORY_MANAGER"].includes(normalizedRole);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4200);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const notify = (message, type = "success") => setToast({ message, type });
  const pageTitle =
    visibleNavItems.find((item) => item.to === location.pathname)?.label ||
    "Workspace";

  if (!account) {
    if (location.pathname === "/login")
      return (
        <AuthPage
          mode="login"
          onAuthenticated={(user) => {
            localStorage.setItem("bookstore-account", JSON.stringify(user));
            setAccount(user);
            navigate("/");
          }}
        />
      );
    if (location.pathname === "/signup")
      return (
        <AuthPage
          mode="signup"
          onAuthenticated={(user) => {
            localStorage.setItem("bookstore-account", JSON.stringify(user));
            setAccount(user);
            navigate("/");
          }}
        />
      );
    return <LandingPage />;
  }

  return (
    <div className="app-shell" style={{ "--brand-primary": configuredClient?.primary_color || "#236d49", "--brand-secondary": configuredClient?.secondary_color || "#d9f0e1" }}>
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark">
            <BookOpen size={19} strokeWidth={2.5} />
          </div>
          <div>
            <strong>{configuredClient?.pos_name || "Bookstore"}</strong>
            <span>operations</span>
          </div>
          <button
            className="icon-button mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>
        <div className="store-switcher">
          <span className="store-dot">
            <Store size={15} />
          </span>
          {canSwitchBranches && availableBranches.length > 1 ? (
            <label className="branch-selector">
              <select
                value={configuredBranch?.id || ""}
                onChange={(event) => {
                  const nextBranch = event.target.value;
                  setSelectedBranchId(nextBranch);
                  localStorage.setItem("bookstore-branch-id", nextBranch);
                  queryClient.invalidateQueries();
                }}
                aria-label="Active branch"
              >
                {availableBranches.map((branch) => <option key={branch.id} value={branch.id}>{branch.name}</option>)}
              </select>
              <small>{configuredBranch?.address || "Active branch"}</small>
            </label>
          ) : (
            <span>
              <b>{configuredBranch?.name || configuredClient?.name || "Main branch"}</b>
              <small>{configuredBranch?.address || "Client workspace"}</small>
            </span>
          )}
          {!canSwitchBranches || availableBranches.length <= 1 ? <ChevronDown size={15} /> : null}
        </div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          <p className="nav-label">Workspace</p>
          {visibleNavItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
              {label === "Point of sale" && <kbd>⌘P</kbd>}
            </NavLink>
          ))}
          {(["OWNER", "ADMIN"].includes(normalizedRole)) && <>
            <p className="nav-label nav-label-spaced">Manage</p>
            <NavLink
              to="/settings"
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            >
              <Settings size={18} />
              <span>Settings</span>
            </NavLink>
          </>}
        </nav>
        <div className="sidebar-footer">
          <div className="help-row">
            <CircleHelp size={17} />
            <span>Need help?</span>
            <span className="online-dot" />
          </div>
          <div className="user-card">
            <div className="avatar">{initials(account.full_name)}</div>
            <div>
              <b>{account.full_name}</b>
              <small>{account.role_name || role} · Online</small>
            </div>
            <button
              className="sidebar-signout"
              onClick={() => {
                localStorage.removeItem("bookstore-account");
                localStorage.removeItem("bookstore-branch-id");
                queryClient.clear();
                setAccount(null);
                setSelectedBranchId("");
                navigate("/login", { replace: true });
              }}
              aria-label="Sign out"
            >
              <LogOut size={15} />
              <span>Log out</span>
            </button>
          </div>
        </div>
      </aside>
      {sidebarOpen && (
        <button
          className="sidebar-scrim"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close navigation"
        />
      )}
      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-button menu-toggle"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={21} />
          </button>
          <div className="breadcrumbs">
            <span>{configuredClient?.pos_name || configuredClient?.name || "Bookstore"}</span>
            <span>/</span>
            <b>{pageTitle}</b>
          </div>
          <div className="topbar-actions">
            <label className="global-search">
              <Search size={17} />
              <input placeholder="Search anything" aria-label="Global search" />
              <kbd>⌘ K</kbd>
            </label>
            <button
              className="icon-button notification-button"
              aria-label="Notifications"
            >
              <Bell size={18} />
              <i />
            </button>
            <div className="top-avatar">{initials(account.full_name)}</div>
          </div>
        </header>
        <div className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard notify={notify} />} />
            <Route path="/pos" element={<POS notify={notify} />} />
            <Route path="/sales" element={<SalesHistory />} />
            <Route path="/returns" element={<Returns notify={notify} />} />
            <Route path="/products" element={<Products />} />
            <Route path="/inventory" element={<Inventory notify={notify} />} />
            <Route path="/customers" element={<Customers notify={notify} />} />
            <Route path="/reports" element={<Reports />} />
            <Route
              path="/settings"
              element={<SettingsPage notify={notify} />}
            />
            <Route path="*" element={<EmptyPage title="Page not found" />} />
          </Routes>
        </div>
      </main>
      {toast && (
        <div className={`toast ${toast.type}`}>
          <span className="toast-icon">
            {toast.type === "error" ? <X size={15} /> : <Check size={15} />}
          </span>
          {toast.message}
        </div>
      )}
    </div>
  );
}

function LandingPage() {
  return (
    <div className="public-page">
      <header className="public-nav">
        <div className="public-brand">
          <span className="brand-mark">
            <BookOpen size={19} />
          </span>
          <strong>Bookstore</strong>
        </div>
        <div className="public-nav-actions">
          <Link className="text-button" to="/login">
            Sign in
          </Link>
          <Link className="button primary" to="/signup">
            Create account
          </Link>
        </div>
      </header>
      <main className="landing-main">
        <section className="landing-copy">
          <p className="eyebrow">A calmer way to run your shelves</p>
          <h1>Every sale, title, and customer in one place.</h1>
          <p>
            Bookstore gives your team a clear counter for selling books,
            tracking stock, managing returns, and understanding what readers
            love.
          </p>
          <div className="landing-actions">
            <Link className="button primary" to="/signup">
              <UserRound size={16} /> Start your workspace
            </Link>
            <Link className="text-link" to="/login">
              Already have an account <ArrowDownToLine size={14} />
            </Link>
          </div>
        </section>
        <section
          className="landing-preview"
          aria-label="Bookstore workspace preview"
        >
          <div className="preview-window">
            <div className="preview-top">
              <span />
              <span />
              <span />
            </div>
            <div className="preview-body">
              <div className="preview-sidebar">
                <span className="preview-logo">
                  <BookOpen size={14} />
                </span>
                <i />
                <i />
                <i />
                <i />
              </div>
              <div className="preview-content">
                <small>OPERATIONS DASHBOARD</small>
                <h2>Good books, well run.</h2>
                <div className="preview-metrics">
                  <b>Live titles</b>
                  <b>Fast sales</b>
                  <b>Stock tracked</b>
                </div>
                <div className="preview-chart">
                  <small>
                    Secure workspace ready for your team
                  </small>
                </div>
              </div>
            </div>
          </div>
          <div className="landing-note">
            <span className="status-dot" /> Live inventory · real-time checkout
          </div>
        </section>
      </main>
      <footer className="public-footer">
        <span>Bookstore operations</span>
        <span>Built for independent booksellers</span>
      </footer>
    </div>
  );
}

function AuthPage({ mode, onAuthenticated }) {
  const isSignup = mode === "signup";
  const [isCashierPin, setIsCashierPin] = useState(false);
  const [form, setForm] = useState(
    isSignup
      ? { company_name: "", pos_name: "", full_name: "", username: "", email: "", password: "", password_confirmation: "" }
      : { login: "", password: "" },
  );
  const [error, setError] = useState("");
  const mutation = useMutation({
    mutationFn: isSignup ? authApi.signup : isCashierPin ? authApi.cashierLogin : authApi.login,
    onSuccess: onAuthenticated,
    onError: (requestError) => setError(requestError.message),
  });
  const update = (field, value) =>
    setForm((current) => ({ ...current, [field]: value }));
  return (
    <div className="auth-page">
      <Link className="auth-brand" to="/">
        <span className="brand-mark">
          <BookOpen size={19} />
        </span>
        <strong>Bookstore</strong>
      </Link>
      <div className="auth-layout">
        <section className="auth-aside">
          <p className="eyebrow">
            {isSignup ? "Your store, connected" : "Welcome back"}
          </p>
          <h1>
            {isSignup
              ? "Build a better day at the counter."
              : "Pick up where your store left off."}
          </h1>
          <p>
            Access live sales, inventory, customer profiles, returns, and
            reports from one focused workspace.
          </p>
          <div className="auth-aside-rule">
            <span className="status-dot" /> Secure account access
          </div>
        </section>
        <section className="auth-card">
          <div className="auth-card-heading">
            <p className="eyebrow">
              {isSignup ? "Create your account" : isCashierPin ? "Cashier access" : "Sign in to Bookstore"}
            </p>
            <h2>{isSignup ? "Start running your store" : "Good to see you"}</h2>
            <p>
                {isSignup
                ? "Set up your operations account in a minute."
                : isCashierPin ? "Use the cashier username and PIN assigned by your administrator." : "Use your bookstore username or email."}
            </p>
          </div>
          {error && <div className="auth-error">{error}</div>}
          <form
            onSubmit={(event) => {
              event.preventDefault();
              setError("");
              if (isSignup && form.password !== form.password_confirmation) {
                setError("Passwords do not match.");
                return;
              }
              mutation.mutate(form);
            }}
          >
            {isSignup && (
              <>
                <label className="form-field">
                  <span>Company name</span>
                  <input
                    value={form.company_name}
                    onChange={(event) => update("company_name", event.target.value)}
                    autoComplete="organization"
                    placeholder="River Street Books"
                    required
                  />
                </label>
                <label className="form-field">
                  <span>POS name</span>
                  <input
                    value={form.pos_name}
                    onChange={(event) => update("pos_name", event.target.value)}
                    placeholder="River Street POS"
                    required
                  />
                </label>
              </>
            )}
            {isSignup && (
              <label className="form-field">
                <span>Full name</span>
                <input
                  value={form.full_name}
                  onChange={(event) => update("full_name", event.target.value)}
                  autoComplete="name"
                  required
                />
              </label>
            )}
            <label className="form-field">
              <span>{isSignup || !isCashierPin ? isSignup ? "Username" : "Username or email" : "Cashier username"}</span>
              <input
                value={isSignup ? form.username : isCashierPin ? form.username : form.login}
                onChange={(event) =>
                  update(isSignup || isCashierPin ? "username" : "login", event.target.value)
                }
                autoComplete="username"
                required
              />
            </label>
            {isSignup && (
              <label className="form-field">
                <span>Email</span>
                <input
                  type="email"
                  value={form.email}
                  onChange={(event) => update("email", event.target.value)}
                  autoComplete="email"
                  required
                />
              </label>
            )}
            <label className="form-field">
              <span>{isCashierPin ? "Login PIN" : "Password"}</span>
              <input
                type="password"
                inputMode={isCashierPin ? "numeric" : undefined}
                value={isCashierPin ? form.pin || "" : form.password}
                onChange={(event) => update(isCashierPin ? "pin" : "password", isCashierPin ? event.target.value.replace(/\D/g, "") : event.target.value)}
                autoComplete={isSignup ? "new-password" : "current-password"}
                minLength={isCashierPin ? 4 : isSignup ? 8 : undefined}
                required
              />
            </label>
            {isSignup && <label className="form-field">
              <span>Confirm password</span>
              <input type="password" value={form.password_confirmation} onChange={(event) => update("password_confirmation", event.target.value)} autoComplete="new-password" minLength="8" required />
            </label>}
            {!isSignup && <button type="button" className="text-button" onClick={() => { setIsCashierPin(!isCashierPin); setForm(isCashierPin ? { login: "", password: "" } : { username: "", pin: "" }); setError(""); }}>{isCashierPin ? "Use administrator password" : "Cashier login with PIN"}</button>}
            <button
              className="button primary wide"
              disabled={mutation.isPending}
            >
              {mutation.isPending
                ? "Please wait…"
                : isSignup
                  ? "Create account"
                  : "Sign in"}
              <ArrowDownToLine size={16} />
            </button>
          </form>
          <p className="auth-switch">
            {isSignup ? "Already have an account?" : "New to Bookstore?"}{" "}
            <Link to={isSignup ? "/login" : "/signup"}>
              {isSignup ? "Sign in" : "Create an account"}
            </Link>
          </p>
        </section>
      </div>
    </div>
  );
}

function PageHeader({ eyebrow, title, description, action }) {
  const displayEyebrow =
    eyebrow === "Tuesday, September 7, 2026"
      ? new Date().toLocaleDateString(undefined, {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric",
        })
      : eyebrow;
  const displayTitle =
    title === "Good morning, Alex" ? "Operations dashboard" : title;
  const displayDescription =
    description === "Here’s the pulse of your bookstore today."
      ? "Live activity from your bookstore database."
      : description;
  return (
    <div className="page-header">
      <div>
        <p className="eyebrow">{displayEyebrow}</p>
        <h1>{displayTitle}</h1>
        {displayDescription && (
          <p className="page-description">{displayDescription}</p>
        )}
      </div>
      {action}
    </div>
  );
}

function QueryState({ query, children, empty = "Nothing here yet." }) {
  if (query.isLoading)
    return (
      <div className="loading-grid">
        <div className="skeleton skeleton-lg" />
        <div className="skeleton skeleton-lg" />
        <div className="skeleton skeleton-lg" />
      </div>
    );
  if (query.isError)
    return (
      <div className="state-panel error-state">
        <Archive size={25} />
        <b>Couldn’t load this view</b>
        <span>{query.error.message}</span>
        <button className="button secondary" onClick={() => query.refetch()}>
          <RefreshCw size={15} /> Try again
        </button>
      </div>
    );
  if (!Array.isArray(query.data) || !query.data.length)
    return (
      <div className="state-panel">
        <Package size={25} />
        <b>{empty}</b>
        <span>Connect your first record to see it here.</span>
      </div>
    );
  return children;
}

function Dashboard({ notify }) {
  const sales = useQuery({ queryKey: ["sales"], queryFn: () => salesApi.list() });
  const inventory = useQuery({
    queryKey: ["inventory"],
    queryFn: () => inventoryApi.list(),
  });
  const completed = (sales.data || []).filter(
    (sale) => sale.status === "COMPLETED",
  );
  const today = new Date().toISOString().slice(0, 10);
  const todaySales = completed.filter(
    (sale) => sale.sale_date?.slice(0, 10) === today,
  );
  const revenue = todaySales.reduce(
    (sum, sale) => sum + Number(sale.total_amount),
    0,
  );
  const lowStock = (inventory.data || []).filter(
    (item) => Number(item.quantity_on_hand) <= Number(item.reorder_level),
  ).length;
  return (
    <>
      <PageHeader
        eyebrow="Tuesday, September 7, 2026"
        title="Good morning, Alex"
        description="Here’s the pulse of your bookstore today."
        action={
          <Link className="button primary" to="/pos">
            <ShoppingCart size={16} /> Open point of sale
          </Link>
        }
      />
      <div className="metric-grid">
        <Metric
          label="Today’s sales"
          value={money(revenue)}
          delta="Live from completed sales"
          icon={CircleDollarSign}
          tone="green"
        />
        <Metric
          label="Transactions"
          value={todaySales.length}
          delta="Completed today"
          icon={ReceiptText}
          tone="blue"
        />
        <Metric
          label="Average ticket"
          value={money(todaySales.length ? revenue / todaySales.length : 0)}
          delta="Across all sales"
          icon={TrendingUp}
          tone="orange"
        />
        <Metric
          label="Low stock"
          value={lowStock}
          delta={lowStock ? "Needs attention" : "All levels healthy"}
          icon={Package}
          tone="red"
        />
      </div>
      <div className="dashboard-grid">
        <section className="panel sales-panel">
          <div className="panel-heading">
            <div>
              <h2>Sales overview</h2>
              <p>Completed transactions in the current session</p>
            </div>
            <Link to="/reports" className="text-link">
              View report <ArrowDownToLine size={14} />
            </Link>
          </div>
          <SalesSparkline sales={completed} />
        </section>
        <section className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <h2>Recent activity</h2>
              <p>Latest completed transactions</p>
            </div>
            <Link to="/sales" className="text-link">
              View all
            </Link>
          </div>
          <div className="activity-list">
            {completed.slice(0, 5).map((sale) => (
              <div className="activity-item" key={sale.id}>
                <span className="activity-icon">
                  <ReceiptText size={16} />
                </span>
                <div>
                  <b>{sale.sale_number}</b>
                  <small>
                    {sale.status.toLowerCase()} ·{" "}
                    {new Date(sale.sale_date).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </small>
                </div>
                <strong>{money(sale.total_amount)}</strong>
              </div>
            ))}
            {!completed.length && (
              <div className="compact-empty">
                No completed sales yet. <Link to="/pos">Start a sale</Link>
              </div>
            )}
          </div>
        </section>
      </div>
      <section className="quick-strip">
        <div>
          <Sparkles size={18} />
          <div>
            <b>Make today a good reading day.</b>
            <span>Your POS is ready for the next customer.</span>
          </div>
        </div>
        <button
          className="button secondary"
          onClick={() =>
            notify("Use the POS search to scan a title or barcode.")
          }
        >
          View workflow <ArrowDownToLine size={15} />
        </button>
      </section>
    </>
  );
}

function Metric({ label, value, delta, icon: Icon, tone }) {
  return (
    <div className="metric-card">
      <div className={`metric-icon ${tone}`}>
        <Icon size={19} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small className={tone === "red" && value > 0 ? "warn" : ""}>
          {delta}
        </small>
      </div>
    </div>
  );
}
function SalesSparkline({ sales }) {
  const points = sales
    .slice(-7)
    .map((sale, index) => ({
      day: index + 1,
      value: Number(sale.total_amount),
    }));
  const max = Math.max(...points.map((point) => point.value), 1);
  const coordinates = points
    .map(
      (point, index) =>
        `${points.length === 1 ? 350 : (index / (points.length - 1)) * 700},${170 - (point.value / max) * 140}`,
    )
    .join(" ");
  const area = points.length ? `${coordinates} 700,190 0,190` : "";
  return (
    <div className="sparkline-wrap">
      {points.length ? (
        <svg
          className="sparkline"
          viewBox="0 0 700 190"
          preserveAspectRatio="none"
          role="img"
          aria-label="Sales chart"
        >
          <polygon points={area} fill="url(#chartFill)" />
          <polyline
            points={coordinates}
            fill="none"
            stroke="#2f8f62"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <defs>
            <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" stopColor="#79c89e" stopOpacity=".28" />
              <stop offset="1" stopColor="#79c89e" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      ) : (
        <div className="chart-empty">
          <BarChart3 size={24} />
          <span>Complete a sale to see your trend.</span>
        </div>
      )}
      <div className="chart-axis">
        <span>Recent</span>
        <span>Sales</span>
        <span>from</span>
        <span>your</span>
        <span>database</span>
      </div>
    </div>
  );
}

function POS({ notify }) {
  const queryClient = useQueryClient();
  const searchRef = useRef(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [cart, setCart] = useState(() =>
    JSON.parse(localStorage.getItem("pos-cart") || "[]"),
  );
  const [customer, setCustomer] = useState(null);
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [receipt, setReceipt] = useState(null);
  const products = useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.list(),
  });
  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(),
  });
  const customers = useQuery({
    queryKey: ["customers"],
    queryFn: () => customersApi.list(),
  });
  const methods = useQuery({
    queryKey: ["payment-methods"],
    queryFn: () => paymentsApi.methods(),
  });
  useEffect(() => {
    localStorage.setItem("pos-cart", JSON.stringify(cart));
  }, [cart]);
  useEffect(() => {
    searchRef.current?.focus();
  }, []);
  const filtered = (products.data || []).filter(
    (product) =>
      `${product.name} ${product.sku} ${product.barcode || ""}`
        .toLowerCase()
        .includes(search.toLowerCase()) &&
      (category === "all" || product.category === category),
  );
  const subtotal = cart.reduce(
    (sum, item) => sum + Number(item.unit_price) * item.quantity,
    0,
  );
  const addToCart = (product) => {
    const stock = Number(product.inventory?.quantity_on_hand || 0);
    if (!stock) return notify("This title is out of stock.", "error");
    setCart((current) =>
      current.some((item) => item.product === product.id)
        ? current.map((item) =>
            item.product === product.id
              ? { ...item, quantity: Math.min(item.quantity + 1, stock) }
              : item,
          )
        : [
            ...current,
            {
              product: product.id,
              sku: product.sku,
              name: product.name,
              unit_price: product.unit_price,
              stock,
              quantity: 1,
            },
          ],
    );
  };
  const changeQty = (id, amount) =>
    setCart((current) =>
      current.map((item) =>
        item.product === id
          ? {
              ...item,
              quantity: Math.max(
                1,
                Math.min(item.quantity + amount, item.stock),
              ),
            }
          : item,
      ),
    );
  const checkout = useMutation({
    mutationFn: (payload) => salesApi.process(payload),
    onSuccess: (data) => {
      setReceipt(data);
      setCart([]);
      setPaymentOpen(false);
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      notify("Sale completed. Receipt is ready.");
    },
    onError: (error) => notify(error.message, "error"),
  });
  const clearCart = () => {
    setCart([]);
    notify("Cart cleared.");
  };
  if (receipt)
    return <ReceiptView data={receipt} onNewSale={() => setReceipt(null)} />;
  return (
    <>
      <PageHeader
        eyebrow="Front counter"
        title="Point of sale"
        description="Scan a title, build the basket, and take payment."
        action={
          <div className="shortcut-hint">
            <kbd>⌘</kbd>
            <span>+ P to focus search</span>
          </div>
        }
      />
      <div className="pos-layout">
        <section className="pos-catalog">
          <div className="catalog-toolbar">
            <label className="search-field">
              <Search size={18} />
              <input
                ref={searchRef}
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search title, ISBN, SKU or barcode..."
              />
              <kbd>/</kbd>
            </label>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              aria-label="Filter by category"
            >
              <option value="all">All categories</option>
              {(categories.data || []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <button
              className="icon-button bordered"
              aria-label="Filter products"
            >
              <SlidersHorizontal size={17} />
            </button>
          </div>
          <div className="catalog-meta">
            <span>{filtered.length} titles available</span>
            <button className="view-toggle active" aria-label="Grid view">
              <Boxes size={15} />
            </button>
            <button className="view-toggle" aria-label="List view">
              <ClipboardList size={15} />
            </button>
          </div>
          <QueryState query={products} empty="No books found">
            <div className="product-grid">
              {filtered.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAdd={() => addToCart(product)}
                />
              ))}
            </div>
          </QueryState>
        </section>
        <aside className="cart-panel">
          <div className="cart-heading">
            <div>
              <h2>Current sale</h2>
              <span>
                {cart.length} {cart.length === 1 ? "title" : "titles"}
              </span>
            </div>
            <button
              className="text-button danger"
              onClick={clearCart}
              disabled={!cart.length}
            >
              <Trash2 size={14} /> Clear
            </button>
          </div>
          <div className="customer-select">
            <UserRound size={17} />
            <div>
              <span>
                {customer
                  ? `${customer.first_name} ${customer.last_name}`
                  : "Walk-in customer"}
              </span>
              <small>
                {customer
                  ? customer.email || "Customer profile"
                  : "No customer selected"}
              </small>
            </div>
            <select
              value={customer?.id || ""}
              onChange={(event) =>
                setCustomer(
                  customers.data?.find(
                    (item) => item.id === event.target.value,
                  ) || null,
                )
              }
              aria-label="Select customer"
            >
              <option value="">Walk-in</option>
              {(customers.data || []).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.first_name} {item.last_name}
                </option>
              ))}
            </select>
          </div>
          <div className="cart-items">
            {cart.length ? (
              cart.map((item) => (
                <div className="cart-item" key={item.product}>
                  <div className="book-cover small">
                    <BookOpen size={17} />
                  </div>
                  <div className="cart-item-info">
                    <b>{item.name}</b>
                    <small>
                      {item.sku} · {money(item.unit_price)}
                    </small>
                    <div className="quantity-control">
                      <button
                        onClick={() => changeQty(item.product, -1)}
                        aria-label={`Decrease ${item.name}`}
                      >
                        −
                      </button>
                      <span>{item.quantity}</span>
                      <button
                        onClick={() => changeQty(item.product, 1)}
                        aria-label={`Increase ${item.name}`}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  <strong>
                    {money(Number(item.unit_price) * item.quantity)}
                  </strong>
                  <button
                    className="remove-button"
                    onClick={() =>
                      setCart((current) =>
                        current.filter(
                          (entry) => entry.product !== item.product,
                        ),
                      )
                    }
                    aria-label={`Remove ${item.name}`}
                  >
                    <X size={15} />
                  </button>
                </div>
              ))
            ) : (
              <div className="cart-empty">
                <div className="empty-basket">
                  <ShoppingCart size={23} />
                </div>
                <b>Your basket is empty</b>
                <span>Search for a title to start a new sale.</span>
              </div>
            )}
          </div>
          <div className="cart-summary">
            <div>
              <span>Subtotal</span>
              <b>{money(subtotal)}</b>
            </div>
            <div>
              <span>Discount</span>
              <b>K0.00</b>
            </div>
            <div>
              <span>Tax</span>
              <b>Calculated at checkout</b>
            </div>
            <div className="total-row">
              <span>Total due</span>
              <strong>{money(subtotal)}</strong>
            </div>
          </div>
          <button
            className="checkout-button"
            disabled={!cart.length || checkout.isPending || !cashierId}
            onClick={() => setPaymentOpen(true)}
          >
            <CreditCard size={18} />{" "}
            {cashierId
              ? "Continue to payment"
              : "Set VITE_CASHIER_ID to checkout"}
            <span>{money(subtotal)}</span>
          </button>
        </aside>
      </div>
      {paymentOpen && (
        <PaymentModal
          cart={cart}
          subtotal={subtotal}
          customer={customer}
          methods={methods.data || []}
          onClose={() => setPaymentOpen(false)}
          onSubmit={(values) => checkout.mutate(values)}
          loading={checkout.isPending}
        />
      )}
    </>
  );
}

function ProductCard({ product, onAdd }) {
  const stock = Number(product.inventory?.quantity_on_hand || 0);
  const low =
    stock > 0 && stock <= Number(product.inventory?.reorder_level || 0);
  return (
    <article className="product-card">
      <div className="book-cover">
        {product.image ? <img src={product.image} alt="" /> : <BookOpen size={27} />}
        <span>{product.category_name || "BOOK"}</span>
      </div>
      <div className="product-info">
        <div className="product-title">
          <h3>{product.name}</h3>
          <span>{product.sku}</span>
        </div>
        <div className="product-bottom">
          <div>
            <strong>{money(product.unit_price)}</strong>
            <span
              className={stock ? (low ? "stock low" : "stock") : "stock out"}
            >
              {stock ? `${stock} in stock` : "Out of stock"}
            </span>
          </div>
          <button
            className="add-button"
            disabled={!stock}
            onClick={onAdd}
            aria-label={`Add ${product.name}`}
          >
            <Plus size={17} />
          </button>
        </div>
      </div>
    </article>
  );
}

function PaymentModal({
  cart,
  subtotal,
  customer,
  methods,
  onClose,
  onSubmit,
  loading,
}) {
  const [method, setMethod] = useState(methods[0]?.type || "CASH");
  const [tendered, setTendered] = useState(subtotal.toFixed(2));
  const schema = z.object({
    tendered: z.coerce
      .number()
      .min(subtotal, `Enter at least ${money(subtotal)}`),
  });
  const change = Math.max(0, Number(tendered || 0) - subtotal);
  return (
    <div className="modal-backdrop">
      <div className="payment-modal">
        <div className="modal-heading">
          <div>
            <p className="eyebrow">Final step</p>
            <h2>Take payment</h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close payment"
          >
            <X size={19} />
          </button>
        </div>
        <div className="payment-total">
          <span>Total due</span>
          <strong>{money(subtotal)}</strong>
        </div>
        <div className="method-grid">
          {methods.length ? (
            methods.map((item) => (
              <button
                key={item.id}
                className={`method-card ${method === item.type ? "selected" : ""}`}
                onClick={() => setMethod(item.type)}
              >
                <CreditCard size={18} />
                <span>{item.name}</span>
                <small>{item.type.replaceAll("_", " ")}</small>
              </button>
            ))
          ) : (
            <div className="inline-warning">
              Create an active payment method in the backend before checkout.
            </div>
          )}
        </div>
        <label className="form-field">
          <span>Amount received</span>
          <input
            type="number"
            min={subtotal}
            step="0.01"
            value={tendered}
            onChange={(event) => setTendered(event.target.value)}
            autoFocus
          />
        </label>
        <div className="change-box">
          <span>Change due</span>
          <strong>{money(change)}</strong>
        </div>
        <div className="modal-actions">
          <button className="button secondary" onClick={onClose}>
            Back
          </button>
          <button
            className="button primary wide"
            disabled={loading || !methods.length || Number(tendered) < subtotal}
            onClick={() => {
              const valid = schema.safeParse({ tendered });
              if (!valid.success) return;
              onSubmit({
                cashier: cashierId,
                customer: customer?.id || null,
                items: cart.map((item) => ({
                  sku: item.sku,
                  quantity: item.quantity,
                })),
                payment_method_type: method,
                tendered_amount: Number(tendered).toFixed(2),
              });
            }}
          >
            {loading ? "Processing…" : "Complete sale"}
            <Check size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

function ReceiptView({ data, onNewSale }) {
  const sale = data.sale;
  const download = () => {
    const receipt = [
      `Leaf & Ledger`,
      `Receipt ${data.receipt_id}`,
      sale.sale_number,
      new Date(sale.sale_date).toLocaleString(),
      "",
      ...(sale.items || []).map(
        (item) =>
          `${item.quantity} x ${item.product}  ${money(item.line_total)}`,
      ),
      "",
      `Subtotal: ${money(sale.subtotal)}`,
      `Tax: ${money(sale.tax_amount)}`,
      `Total: ${money(sale.total_amount)}`,
    ].join("\n");
    const blob = new Blob([receipt], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${sale.sale_number || "receipt"}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };
  return (
    <div className="receipt-result">
      <div className="result-banner">
        <span className="success-mark">
          <Check size={21} />
        </span>
        <div>
          <p className="eyebrow">Payment approved</p>
          <h1>Sale completed</h1>
          <p>Receipt {data.receipt_id}</p>
        </div>
        <button className="button primary" onClick={onNewSale}>
          <Plus size={16} /> New sale
        </button>
      </div>
      <div className="receipt-paper">
        <div className="receipt-brand">
          <div className="brand-mark">
            <BookOpen size={17} />
          </div>
          <div>
            <b>Leaf & Ledger</b>
            <span>River Street · Main branch</span>
          </div>
        </div>
        <div className="receipt-meta">
          <span>{sale.sale_number}</span>
          <span>{new Date(sale.sale_date).toLocaleString()}</span>
        </div>
        {sale.items?.map((item) => (
          <div className="receipt-line" key={item.id}>
            <span>
              {item.quantity} × {item.product}
            </span>
            <b>{money(item.line_total)}</b>
          </div>
        ))}
        <div className="receipt-rule" />
        <div className="receipt-line">
          <span>Subtotal</span>
          <b>{money(sale.subtotal)}</b>
        </div>
        <div className="receipt-line">
          <span>Tax</span>
          <b>{money(sale.tax_amount)}</b>
        </div>
        <div className="receipt-line total">
          <span>Total</span>
          <b>{money(sale.total_amount)}</b>
        </div>
        <p className="receipt-footer">
          Thank you for supporting independent bookselling.
        </p>
      </div>
      <div className="result-actions">
        <button className="button secondary" onClick={() => window.print()}>
          <ReceiptText size={16} /> Print receipt
        </button>
        <button className="button secondary" onClick={download}>
          <ArrowDownToLine size={16} /> Download
        </button>
      </div>
    </div>
  );
}

function SalesHistory() {
  const sales = useQuery({ queryKey: ["sales"], queryFn: () => salesApi.list() });
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("ALL");
  const rows = (sales.data || []).filter(
    (sale) =>
      sale.sale_number.toLowerCase().includes(search.toLowerCase()) &&
      (status === "ALL" || sale.status === status),
  );
  const exportRows = () => {
    const csv = [
      ["Sale number", "Date", "Cashier", "Status", "Total"],
      ...rows.map((sale) => [
        sale.sale_number,
        sale.sale_date,
        sale.cashier,
        sale.status,
        sale.total_amount,
      ]),
    ]
      .map((row) =>
        row
          .map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`)
          .join(","),
      )
      .join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "sales-history.csv";
    link.click();
    URL.revokeObjectURL(url);
  };
  return (
    <>
      <PageHeader
        eyebrow="Transactions"
        title="Sales history"
        description="A clear view of every completed and in-progress sale."
        action={
          <Link className="button secondary" to="/reports">
            <BarChart3 size={16} /> View reports
          </Link>
        }
      />
      <div className="toolbar-row">
        <label className="search-field compact">
          <Search size={16} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search sale number..."
          />
        </label>
        <select
          value={status}
          onChange={(event) => setStatus(event.target.value)}
        >
          <option value="ALL">All statuses</option>
          <option value="COMPLETED">Completed</option>
          <option value="DRAFT">Draft</option>
        </select>
        <button
          className="button secondary"
          onClick={exportRows}
          disabled={!rows.length}
        >
          <ArrowDownToLine size={15} /> Export
        </button>
      </div>
      <QueryState query={sales} empty="No sales yet">
        <div className="panel data-panel">
          <table>
            <thead>
              <tr>
                <th>Sale number</th>
                <th>Date</th>
                <th>Cashier</th>
                <th>Status</th>
                <th className="align-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((sale) => (
                <tr key={sale.id}>
                  <td>
                    <b>{sale.sale_number}</b>
                  </td>
                  <td>{new Date(sale.sale_date).toLocaleString()}</td>
                  <td className="muted">{sale.cashier}</td>
                  <td>
                    <StatusBadge value={sale.status} />
                  </td>
                  <td className="align-right">
                    <b>{money(sale.total_amount)}</b>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && (
            <div className="compact-empty">
              No sales match the current filters.
            </div>
          )}
        </div>
      </QueryState>
    </>
  );
}
function StatusBadge({ value }) {
  return (
    <span className={`status-badge ${value.toLowerCase()}`}>
      <i />
      {value.toLowerCase()}
    </span>
  );
}

function ReturnsLegacy({ notify }) {
  const [receiptNumber, setReceiptNumber] = useState("");
  const [items, setItems] = useState("");
  const [reason, setReason] = useState("");
  const [cashier, setCashier] = useState(cashierId);
  const mutation = useMutation({
    mutationFn: returnsApi.process,
    onSuccess: () => {
      notify("Return completed and inventory restored.");
      setReceiptNumber("");
      setItems("");
      setReason("");
    },
    onError: (error) => notify(error.message, "error"),
  });
  return (
    <>
      <PageHeader
        eyebrow="Aftercare"
        title="Returns"
        description="Find a receipt and put the right books back on the shelf."
      />
      <div className="workflow-layout">
        <section className="panel workflow-card">
          <div className="workflow-step">
            <span>01</span>
            <div>
              <h2>Locate original receipt</h2>
              <p>Search by the receipt number printed at checkout.</p>
            </div>
          </div>
          <label className="form-field">
            <span>Receipt number</span>
            <input
              value={receiptNumber}
              onChange={(event) => setReceiptNumber(event.target.value)}
            />
          </label>
          <label className="form-field">
            <span>Sale item ID</span>
            <input
              value={items}
              onChange={(event) => setItems(event.target.value)}
            />
          </label>
          <label className="form-field">
            <span>Reason</span>
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
          </label>
          <button
            className="button primary wide"
            disabled={
              mutation.isPending || !cashier || !receiptNumber || !items
            }
            onClick={() =>
              mutation.mutate({
                cashier,
                receipt_number: receiptNumber,
                items: [{ sale_item_id: items, quantity: 1, reason }],
                refund_method_type: "CASH",
                return_reason: reason,
              })
            }
          >
            Complete return
          </button>
        </section>
      </div>
    </>
  );
}

function Returns({ notify }) {
  const sales = useQuery({ queryKey: ["sales"], queryFn: () => salesApi.list() });
  const receipts = useQuery({
    queryKey: ["receipts"],
    queryFn: receiptsApi.list,
  });
  const [saleId, setSaleId] = useState("");
  const [itemId, setItemId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [reason, setReason] = useState("");
  const sale = (sales.data || []).find((item) => item.id === saleId);
  const receipt = (receipts.data || []).find((item) => item.sale === saleId);
  const items = sale?.items || [];
  const mutation = useMutation({
    mutationFn: returnsApi.process,
    onSuccess: () => {
      notify("Return completed and inventory restored.");
      setSaleId("");
      setItemId("");
      setQuantity("1");
      setReason("");
    },
    onError: (error) => notify(error.message, "error"),
  });
  const loading = sales.isLoading || receipts.isLoading;
  return (
    <>
      <PageHeader
        eyebrow="Aftercare"
        title="Returns"
        description="Choose a completed sale from the database and return an item."
      />
      <div className="workflow-layout">
        <section className="panel workflow-card">
          <label className="form-field">
            <span>Completed sale</span>
            <select
              value={saleId}
              onChange={(event) => {
                setSaleId(event.target.value);
                setItemId("");
              }}
            >
              <option value="">Select a sale</option>
              {(sales.data || [])
                .filter((item) => item.status === "COMPLETED")
                .map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.sale_number} · {money(item.total_amount)}
                  </option>
                ))}
            </select>
          </label>
          <label className="form-field">
            <span>Item</span>
            <select
              value={itemId}
              onChange={(event) => setItemId(event.target.value)}
              disabled={!sale}
            >
              <option value="">Select an item</option>
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.product_name || item.product_sku || item.product} · sold{" "}
                  {item.quantity}
                </option>
              ))}
            </select>
          </label>
          <label className="form-field">
            <span>Quantity</span>
            <input
              type="number"
              min="0.001"
              max={items.find((item) => item.id === itemId)?.quantity || 1}
              step="0.001"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              disabled={!itemId}
            />
          </label>
          <label className="form-field">
            <span>Reason</span>
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              placeholder="Why is this book being returned?"
              rows="3"
            />
          </label>
          <p className="form-hint">
            {receipt
              ? `Receipt: ${receipt.receipt_number}`
              : loading
                ? "Loading completed sales..."
                : "Select a completed sale to find its receipt."}
          </p>
          <button
            className="button primary wide"
            disabled={
              mutation.isPending ||
              !cashierId ||
              !receipt ||
              !itemId ||
              Number(quantity) <= 0
            }
            onClick={() =>
              mutation.mutate({
                cashier: cashierId,
                receipt_number: receipt.receipt_number,
                items: [
                  { sale_item_id: itemId, quantity: Number(quantity), reason },
                ],
                refund_method_type: "CASH",
                return_reason: reason,
              })
            }
          >
            {mutation.isPending ? "Processing return…" : "Complete return"}
            <Check size={16} />
          </button>
        </section>
        <aside className="panel info-panel">
          <div className="info-icon">
            <ArrowLeftRight size={20} />
          </div>
          <h2>Returns stay traceable</h2>
          <p>
            The selected sale, receipt, item, refund, and inventory restoration
            are recorded by the backend.
          </p>
        </aside>
      </div>
    </>
  );
}

function ProductFormModal({ mode = "create", product = null, categories, onClose, onSaved }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: product?.name || "",
    author: product?.author || "",
    edition: product?.edition || "",
    publisher: product?.publisher || "",
    isbn: product?.isbn || "",
    publication_date: product?.publication_date || "",
    language: product?.language || "English",
    page_count: product?.page_count ?? "",
    sku: product?.sku || "",
    category: product?.category || "",
    unit_price: product?.unit_price ?? "",
    cost_price: product?.cost_price ?? "",
    tax_rate: String(product?.tax_rate ?? "0"),
    barcode: product?.barcode || "",
    description: product?.description || "",
    image: null,
  });

  useEffect(() => {
    setForm({
      name: product?.name || "",
      author: product?.author || "",
      edition: product?.edition || "",
      publisher: product?.publisher || "",
      isbn: product?.isbn || "",
      publication_date: product?.publication_date || "",
      language: product?.language || "English",
      page_count: product?.page_count ?? "",
      sku: product?.sku || "",
      category: product?.category || "",
      unit_price: product?.unit_price ?? "",
      cost_price: product?.cost_price ?? "",
      tax_rate: String(product?.tax_rate ?? "0"),
      barcode: product?.barcode || "",
      description: product?.description || "",
      image: null,
    });
  }, [product]);

  const mutation = useMutation({
    mutationFn:
      mode === "edit"
        ? (payload) => productsApi.update(product.id, payload)
        : productsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onSaved?.();
      onClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => productsApi.remove(product.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onSaved?.();
      onClose();
    },
  });

  const update = (field, value) =>
    setForm((current) => ({ ...current, [field]: value }));

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = {
      ...form,
      is_active: true,
      unit_price: Number(form.unit_price),
      cost_price: Number(form.cost_price),
      tax_rate: Number(form.tax_rate),
      page_count: form.page_count ? Number(form.page_count) : null,
      image: form.image,
    };
    mutation.mutate(payload);
  };

  return (
    <div className="modal-backdrop">
      <form className="small-modal" onSubmit={handleSubmit}>
        <div className="modal-heading">
          <h2>{mode === "edit" ? "Edit product" : "New product"}</h2>
          <button type="button" className="icon-button" onClick={onClose}>
            <X size={18} />
          </button>
        </div>
        {[
          ["name", "Title"],
          ["author", "Author"],
          ["edition", "Edition"],
          ["publisher", "Publisher"],
          ["isbn", "ISBN"],
          ["publication_date", "Publication date"],
          ["language", "Language"],
          ["page_count", "Page count"],
          ["sku", "SKU"],
          ["unit_price", "Selling price"],
          ["cost_price", "Cost price"],
          ["barcode", "Barcode"],
        ].map(([field, label]) => (
          <label className="form-field" key={field}>
            <span>{label}</span>
            <input
              required={field === "name" || field === "sku" || field === "unit_price" || field === "cost_price"}
              type={field.includes("price") || field === "page_count" ? "number" : field === "publication_date" ? "date" : "text"}
              min={field === "page_count" ? "1" : undefined}
              step={field.includes("price") ? "0.01" : field === "page_count" ? "1" : undefined}
              value={form[field]}
              onChange={(event) => update(field, event.target.value)}
            />
          </label>
        ))}
        <label className="form-field">
          <span>Category</span>
          <select
            required
            value={form.category}
            onChange={(event) => update("category", event.target.value)}
          >
            <option value="">Select category</option>
            {(categories.data || []).map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span>Description</span>
          <textarea
            value={form.description}
            onChange={(event) => update("description", event.target.value)}
            rows="2"
          />
        </label>
        <label className="form-field">
          <span>Cover image</span>
          <input
            type="file"
            accept="image/*"
            onChange={(event) =>
              update("image", event.target.files?.[0] || null)
            }
          />
        </label>
        <div className="modal-actions">
          {mode === "edit" && (
            <button
              type="button"
              className="button secondary"
              disabled={deleteMutation.isPending}
              onClick={() => deleteMutation.mutate()}
            >
              {deleteMutation.isPending ? "Deleting…" : "Delete"}
            </button>
          )}
          <button
            type="submit"
            className="button primary wide"
            disabled={mutation.isPending || !categories.data?.length}
          >
            {mutation.isPending
              ? mode === "edit"
                ? "Saving…"
                : "Creating…"
              : mode === "edit"
                ? "Save changes"
                : "Create product"}
            <Check size={16} />
          </button>
        </div>
      </form>
    </div>
  );
}

function ProductCreateButton() {
  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(),
  });
  const [open, setOpen] = useState(false);

  return (
    <>
      <button className="button primary" onClick={() => setOpen(true)}>
        <Plus size={16} /> Add product
      </button>
      {open && (
        <ProductFormModal
          mode="create"
          categories={categories}
          onClose={() => setOpen(false)}
          onSaved={() => setOpen(false)}
        />
      )}
    </>
  );
}

function Products() {
  const query = useQuery({ queryKey: ["products"], queryFn: () => productsApi.list() });
  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(),
  });
  const [search, setSearch] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const products = (query.data || []).filter((product) =>
    `${product.name} ${product.sku} ${product.barcode || ""}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        eyebrow="Catalogue"
        title="Products"
        description="Your books, prices, categories, and availability."
        action={<ProductCreateButton />}
      />
      <div className="toolbar-row">
        <label className="search-field compact">
          <Search size={16} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search title, SKU or barcode..."
          />
        </label>
        <span className="toolbar-count">{products.length} titles</span>
      </div>
      <QueryState query={query} empty="No products in the catalogue">
        <div className="product-table panel data-panel">
          <table>
            <thead>
              <tr>
                <th>Book</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id} onClick={() => setSelectedProduct(product)} style={{ cursor: "pointer" }}>
                  <td>
                    <div className="table-book">
                      <span className="book-cover tiny">
                        <BookOpen size={14} />
                      </span>
                      <b>{product.name}</b>
                    </div>
                  </td>
                  <td className="muted">{product.sku}</td>
                  <td>{product.category_name || product.category}</td>
                  <td>
                    <b>{money(product.unit_price)}</b>
                  </td>
                  <td>{product.inventory?.quantity_on_hand || 0}</td>
                  <td>
                    <StatusBadge
                      value={product.is_active ? "Active" : "Inactive"}
                    />
                  </td>
                  <td onClick={(event) => event.stopPropagation()}>
                    <button
                      className="button secondary compact"
                      onClick={() => setSelectedProduct(product)}
                    >
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!products.length && (
            <div className="compact-empty">
              No products match the current search.
            </div>
          )}
        </div>
      </QueryState>
      {selectedProduct && (
        <ProductFormModal
          mode="edit"
          product={selectedProduct}
          categories={categories}
          onClose={() => setSelectedProduct(null)}
          onSaved={() => setSelectedProduct(null)}
        />
      )}
    </>
  );
}

function Inventory({ notify }) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["inventory"],
    queryFn: () => inventoryApi.list(),
  });
  const [form, setForm] = useState({
    sku: "",
    quantity_change: "",
    reason: "",
    adjustment_type: "RESTOCK",
  });
  const operatorId = getActiveCashierId();
  const mutation = useMutation({
    mutationFn: inventoryApi.adjust,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      notify("Inventory adjustment saved.");
      setForm({
        sku: "",
        quantity_change: "",
        reason: "",
        adjustment_type: "RESTOCK",
      });
    },
    onError: (error) => notify(error.message, "error"),
  });
  return (
    <>
      <PageHeader
        eyebrow="Stockroom"
        title="Inventory"
        description="Keep the shelves healthy and every adjustment accountable."
        action={
          <button
            className="button primary"
            onClick={() =>
              document
                .getElementById("adjust-stock")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            <Plus size={16} /> Adjust stock
          </button>
        }
      />
      <div className="metric-grid compact-metrics">
        <Metric
          label="Tracked titles"
          value={query.data?.length || 0}
          delta="Across catalogue"
          icon={BookOpen}
          tone="blue"
        />
        <Metric
          label="Low stock"
          value={
            (query.data || []).filter(
              (item) =>
                Number(item.quantity_on_hand) <= Number(item.reorder_level),
            ).length
          }
          delta="Reorder soon"
          icon={TrendingUp}
          tone="orange"
        />
        <Metric
          label="Out of stock"
          value={
            (query.data || []).filter(
              (item) => Number(item.quantity_on_hand) === 0,
            ).length
          }
          delta="Needs attention"
          icon={Archive}
          tone="red"
        />
      </div>
      <div className="inventory-layout">
        <div className="panel data-panel">
          <div className="panel-heading">
            <div>
              <h2>Stock levels</h2>
              <p>Live quantity on hand from the inventory service.</p>
            </div>
          </div>
          <QueryState query={query} empty="No inventory records">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>On hand</th>
                  <th>Reorder level</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(query.data || []).map((item) => (
                  <tr key={item.id}>
                    <td>
                      <b>{item.product_name || item.product}</b>
                    </td>
                    <td className="muted">
                      {item.product_sku || item.product}
                    </td>
                    <td>
                      <b>{item.quantity_on_hand}</b>
                    </td>
                    <td>{item.reorder_level}</td>
                    <td>
                      <StatusBadge
                        value={
                          Number(item.quantity_on_hand) === 0
                            ? "Out"
                            : Number(item.quantity_on_hand) <=
                                Number(item.reorder_level)
                              ? "Low"
                              : "Healthy"
                        }
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </QueryState>
        </div>
        <section className="panel adjust-card" id="adjust-stock">
          <div className="panel-heading">
            <div>
              <h2>Add inventory</h2>
              <p>Add received units to a product and keep stock levels current.</p>
            </div>
            <ClipboardList size={20} />
          </div>
          <div className="form-field">
            <span>SKU</span>
            <select
              value={form.sku}
              onChange={(event) =>
                setForm({ ...form, sku: event.target.value })
              }
            >
              <option value="">Select product</option>
              {(query.data || []).map((item) => (
                <option key={item.id} value={item.product_sku}>
                  {item.product_name} ({item.product_sku})
                </option>
              ))}
            </select>
          </div>
          <div className="split-fields">
            <label className="form-field">
              <span>Movement</span>
                <input value="Restock" readOnly />
            </label>
            <label className="form-field">
              <span>Units to add</span>
              <input
                type="number"
                step="0.001"
                min="0.001"
                value={form.quantity_change}
                onChange={(event) =>
                  setForm({ ...form, quantity_change: event.target.value })
                }
                placeholder="10"
              />
            </label>
          </div>
          <label className="form-field">
            <span>Reason</span>
            <textarea
              rows="3"
              value={form.reason}
              onChange={(event) =>
                setForm({ ...form, reason: event.target.value })
              }
              placeholder="New delivery, damaged copy..."
            />
          </label>
          {mutation.isError && (
            <div className="inline-warning">{mutation.error.message}</div>
          )}
          <button
            className="button primary wide"
            disabled={
              mutation.isPending ||
              !form.sku ||
              !form.quantity_change ||
              !form.reason ||
              !operatorId
            }
            onClick={() =>
              mutation.mutate({
                ...form,
                adjusted_by: operatorId,
                quantity_change: Number(form.quantity_change),
              })
            }
          >
            {mutation.isPending ? "Saving…" : "Save adjustment"}
            <Check size={16} />
          </button>
        </section>
      </div>
    </>
  );
}

function Customers({ notify }) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["customers"],
    queryFn: () => customersApi.list(),
  });
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
  });
  const mutation = useMutation({
    mutationFn: customersApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      setOpen(false);
      setForm({ first_name: "", last_name: "", email: "", phone: "" });
      notify("Customer profile created.");
    },
    onError: (error) => notify(error.message, "error"),
  });
  return (
    <>
      <PageHeader
        eyebrow="Relationships"
        title="Customers"
        description="Keep regular readers recognised at the counter."
        action={
          <button className="button primary" onClick={() => setOpen(true)}>
            <Plus size={16} /> Add customer
          </button>
        }
      />
      <QueryState query={query} empty="No customer profiles">
        <div className="customer-grid">
          {query.data.map((customer) => (
            <div className="panel customer-card" key={customer.id}>
              <div className="avatar large">
                {initials(`${customer.first_name} ${customer.last_name}`)}
              </div>
              <div>
                <h2>
                  {customer.first_name} {customer.last_name}
                </h2>
                <p>
                  {customer.email || "No email"} ·{" "}
                  {customer.phone || "No phone"}
                </p>
                <span>{customer.loyalty_points} loyalty points</span>
              </div>
            </div>
          ))}
        </div>
      </QueryState>
      {open && (
        <div className="modal-backdrop">
          <div className="small-modal">
            <div className="modal-heading">
              <h2>New customer</h2>
              <button className="icon-button" onClick={() => setOpen(false)}>
                <X size={18} />
              </button>
            </div>
            {["first_name", "last_name", "email", "phone"].map((field) => (
              <label className="form-field" key={field}>
                <span>{field.replace("_", " ")}</span>
                <input
                  value={form[field]}
                  onChange={(event) =>
                    setForm({ ...form, [field]: event.target.value })
                  }
                />
              </label>
            ))}
            <button
              className="button primary wide"
              disabled={
                mutation.isPending || !form.first_name || !form.last_name
              }
              onClick={() => mutation.mutate(form)}
            >
              {mutation.isPending ? "Saving…" : "Create customer"}
              <Check size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}

function Reports() {
  const [reportType, setReportType] = useState("sales");
  const [filters, setFilters] = useState({
    start_date: new Date().toISOString().slice(0, 10),
    end_date: new Date().toISOString().slice(0, 10),
    product_name: "",
  });
  const [sortConfig, setSortConfig] = useState({ key: "sale_date", direction: "desc" });

  const query = useQuery({
    queryKey: ["report", reportType, filters],
    queryFn: () => reportsApi.fetch({ ...filters, report_type: reportType }),
  });

  const report = query.data;
  const rows = report?.rows || [];
  const metrics = report?.totals || {};

  const reportTitleMap = {
    sales: "Sales report",
    stock_balance: "Stock balance report",
    stock_value: "Stock value report",
  };
  const reportDescriptionMap = {
    sales: "Sales movement, pricing, and payment performance in a spreadsheet view.",
    stock_balance: "Inventory balance and movement across the selected date range.",
    stock_value: "Current inventory valuation by item and product name.",
  };
  const salesColumns = [
    "sale_number",
    "sale_date",
    "product_name",
    "sku",
    "quantity",
    "unit_price",
    "gross_sales",
    "discount_amount",
    "tax_amount",
    "line_total",
  ];
  const inventoryColumns = [
    "product_name",
    "sku",
    "category",
    "quantity_on_hand",
    "reorder_level",
    "movement_in_period",
    "unit_price",
    "stock_value",
    "last_updated",
  ];
  const valueColumns = [
    "product_name",
    "sku",
    "category",
    "quantity_on_hand",
    "unit_price",
    "stock_value",
    "reorder_level",
  ];
  const columns =
    reportType === "sales"
      ? salesColumns
      : reportType === "stock_value"
        ? valueColumns
        : inventoryColumns;

  useEffect(() => {
    setSortConfig({
      key:
        reportType === "sales"
          ? "sale_date"
          : reportType === "stock_value"
            ? "stock_value"
            : "product_name",
      direction: "desc",
    });
  }, [reportType]);

  const handleSort = (columnKey) => {
    setSortConfig((current) => ({
      key: columnKey,
      direction:
        current.key === columnKey && current.direction === "asc" ? "desc" : "asc",
    }));
  };

  const sortedRows = useMemo(() => {
    const data = [...rows];
    if (!sortConfig.key) return data;
    data.sort((a, b) => {
      const first = a[sortConfig.key];
      const second = b[sortConfig.key];
      const numericA = Number(first ?? 0);
      const numericB = Number(second ?? 0);
      const isNumeric =
        !Number.isNaN(numericA) && !Number.isNaN(numericB) &&
        (typeof first === "number" || typeof second === "number" ||
          String(first).trim() !== "" && String(second).trim() !== "");
      if (isNumeric) {
        return sortConfig.direction === "asc" ? numericA - numericB : numericB - numericA;
      }
      const left = String(first ?? "").toLowerCase();
      const right = String(second ?? "").toLowerCase();
      return sortConfig.direction === "asc"
        ? left.localeCompare(right)
        : right.localeCompare(left);
    });
    return data;
  }, [rows, sortConfig]);

  const formatCellValue = (value) => {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "number") {
      return Number(value).toLocaleString(undefined, {
        maximumFractionDigits: 2,
      });
    }
    if (value instanceof Date) return value.toLocaleString();
    return value;
  };

  return (
    <>
      <PageHeader
        eyebrow="Business intelligence"
        title={reportTitleMap[reportType] || "Reports"}
        description={reportDescriptionMap[reportType] || "Operational reporting."}
        action={
          <div className="export-actions">
            <a
              className="button secondary"
              href={`/api/reports/?report_type=${reportType}&start_date=${filters.start_date}&end_date=${filters.end_date}&product_name=${encodeURIComponent(filters.product_name || "")}&export=csv`}
            >
              <ArrowDownToLine size={15} /> CSV
            </a>
            <a
              className="button secondary"
              href={`/api/reports/?report_type=${reportType}&start_date=${filters.start_date}&end_date=${filters.end_date}&product_name=${encodeURIComponent(filters.product_name || "")}&export=pdf`}
            >
              <FileText size={15} /> PDF
            </a>
          </div>
        }
      />

      <div className="report-filter panel">
        <label className="form-field">
          <span>Report type</span>
          <select
            value={reportType}
            onChange={(event) => setReportType(event.target.value)}
          >
            <option value="sales">Sales report</option>
            <option value="stock_balance">Stock balance report</option>
            <option value="stock_value">Stock value report</option>
          </select>
        </label>
        <label className="form-field">
          <span>From</span>
          <input
            type="date"
            value={filters.start_date}
            onChange={(event) =>
              setFilters({ ...filters, start_date: event.target.value })
            }
          />
        </label>
        <label className="form-field">
          <span>To</span>
          <input
            type="date"
            value={filters.end_date}
            onChange={(event) =>
              setFilters({ ...filters, end_date: event.target.value })
            }
          />
        </label>
        <label className="form-field">
          <span>Item / product name</span>
          <input
            value={filters.product_name}
            onChange={(event) =>
              setFilters({ ...filters, product_name: event.target.value })
            }
            placeholder="Search by product name"
          />
        </label>
      </div>

      {query.isError ? (
        <div className="state-panel error-state">
          <b>Report unavailable</b>
          <span>{query.error.message}</span>
        </div>
      ) : (
        <>
          <div className="metric-grid">
            {reportType === "sales" ? (
              <>
                <Metric label="Gross sales" value={money(metrics.gross_sales)} delta="Before discounts" icon={CircleDollarSign} tone="green" />
                <Metric label="Discounts" value={money(metrics.discounts)} delta="Applied" icon={Tag} tone="orange" />
                <Metric label="Taxes" value={money(metrics.taxes)} delta="Collected" icon={ReceiptText} tone="blue" />
                <Metric label="Net sales" value={money(metrics.net_sales)} delta={`${metrics.transaction_count || 0} transactions`} icon={TrendingUp} tone="green" />
              </>
            ) : (
              <>
                <Metric label="Products" value={metrics.total_products || 0} delta="Tracked titles" icon={BookOpen} tone="blue" />
                <Metric label="Units" value={Number(metrics.total_units || 0).toFixed(2)} delta="On hand" icon={Boxes} tone="green" />
                <Metric label="Stock value" value={money(metrics.total_stock_value)} delta="Current value" icon={CircleDollarSign} tone="orange" />
              </>
            )}
          </div>

          <div className="panel data-panel">
            <div className="panel-heading">
              <div>
                <h2>Spreadsheet view</h2>
                <p>Detailed rows for the selected report.</p>
              </div>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>
                        <button
                          type="button"
                          className="table-sort-button"
                          onClick={() => handleSort(column)}
                        >
                          {column.replaceAll("_", " ")}
                          <span aria-hidden="true">
                            {sortConfig.key === column
                              ? sortConfig.direction === "asc"
                                ? "↑"
                                : "↓"
                              : "↕"}
                          </span>
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.length ? (
                    sortedRows.map((row, index) => (
                      <tr key={`${row.product_name || row.sale_number || "row"}-${index}`}>
                        {columns.map((column) => (
                          <td key={`${column}-${index}`}>
                            {formatCellValue(row[column])}
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={columns.length} className="muted">
                        No rows match the current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
}

function SettingsPage({ notify }) {
  const queryClient = useQueryClient();
  const clientQuery = useQuery({ queryKey: ["managed-client"], queryFn: authApi.client });
  const branchesQuery = useQuery({ queryKey: ["managed-branches"], queryFn: authApi.branches });
  const cashiersQuery = useQuery({ queryKey: ["managed-cashiers"], queryFn: authApi.cashiers });
  const [clientForm, setClientForm] = useState({ name: "", pos_name: "", primary_color: "#236d49", secondary_color: "#d9f0e1" });
  const [branchForm, setBranchForm] = useState({ name: "", code: "", address: "" });
  const [cashierForm, setCashierForm] = useState({ full_name: "", username: "", email: "", branch: "", pin: "" });

  useEffect(() => {
    if (clientQuery.data) setClientForm(clientQuery.data);
  }, [clientQuery.data]);

  const saveClient = useMutation({
    mutationFn: (payload) => clientQuery.data ? authApi.saveClient(payload) : authApi.createClient(payload),
    onSuccess: (data) => { queryClient.setQueryData(["managed-client"], data); notify("POS profile saved."); },
    onError: (error) => notify(error.message, "error"),
  });
  const createBranch = useMutation({
    mutationFn: (payload) => authApi.createBranch({ ...payload, client: clientQuery.data.id }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["managed-branches"] }); setBranchForm({ name: "", code: "", address: "" }); notify("Branch added."); },
    onError: (error) => notify(error.message, "error"),
  });
  const createCashier = useMutation({
    mutationFn: authApi.createCashier,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["managed-cashiers"] }); setCashierForm({ full_name: "", username: "", email: "", branch: "", pin: "" }); notify("Cashier added."); },
    onError: (error) => notify(error.message, "error"),
  });

  if (clientQuery.isLoading) return <div className="state-panel">Loading system management...</div>;
  return (
    <>
      <PageHeader
        eyebrow="System management"
        title="Client onboarding"
        description="Configure the POS identity, branches, and cashier access for this client."
      />
      <div className="management-grid">
        <section className="panel management-card">
          <div className="panel-heading"><div><h2><Palette size={17} /> POS identity</h2><p>Brand the workspace your client sees.</p></div></div>
          <div className="form-grid two-columns">
            <label className="form-field"><span>Client name</span><input value={clientForm.name} onChange={(event) => setClientForm({ ...clientForm, name: event.target.value })} placeholder="River Street Books" /></label>
            <label className="form-field"><span>POS name</span><input value={clientForm.pos_name} onChange={(event) => setClientForm({ ...clientForm, pos_name: event.target.value })} placeholder="River Street POS" /></label>
            <label className="form-field"><span>Primary brand color</span><input type="color" value={clientForm.primary_color} onChange={(event) => setClientForm({ ...clientForm, primary_color: event.target.value })} /></label>
            <label className="form-field"><span>Secondary brand color</span><input type="color" value={clientForm.secondary_color} onChange={(event) => setClientForm({ ...clientForm, secondary_color: event.target.value })} /></label>
          </div>
          <button className="button primary" disabled={saveClient.isPending || !clientForm.name || !clientForm.pos_name} onClick={() => saveClient.mutate(clientForm)}><Check size={16} /> Save POS identity</button>
        </section>

        <section className="panel management-card">
          <div className="panel-heading"><div><h2><Building2 size={17} /> Branches</h2><p>Keep each client location organised.</p></div></div>
          <div className="form-grid two-columns">
            <label className="form-field"><span>Branch name</span><input value={branchForm.name} onChange={(event) => setBranchForm({ ...branchForm, name: event.target.value })} placeholder="Main branch" /></label>
            <label className="form-field"><span>Branch code</span><input value={branchForm.code} onChange={(event) => setBranchForm({ ...branchForm, code: event.target.value.toUpperCase() })} placeholder="MAIN" /></label>
            <label className="form-field full-field"><span>Address</span><input value={branchForm.address} onChange={(event) => setBranchForm({ ...branchForm, address: event.target.value })} placeholder="12 River Street" /></label>
          </div>
          <button className="button secondary" disabled={!clientQuery.data || createBranch.isPending || !branchForm.name || !branchForm.code} onClick={() => createBranch.mutate(branchForm)}><Plus size={16} /> Add branch</button>
          <div className="management-list">{(branchesQuery.data || []).map((branch) => <div className="management-list-row" key={branch.id}><span><b>{branch.name}</b><small>{branch.code} {branch.address && `· ${branch.address}`}</small></span><span className="status-badge">Active</span></div>)}</div>
        </section>

        <section className="panel management-card full-width">
          <div className="panel-heading"><div><h2><UserPlus size={17} /> Cashiers and PIN access</h2><p>Create a cashier login PIN for each branch. PINs are stored securely and are never displayed after saving.</p></div></div>
          <div className="form-grid three-columns">
            <label className="form-field"><span>Full name</span><input value={cashierForm.full_name} onChange={(event) => setCashierForm({ ...cashierForm, full_name: event.target.value })} placeholder="Chanda Banda" /></label>
            <label className="form-field"><span>Username</span><input value={cashierForm.username} onChange={(event) => setCashierForm({ ...cashierForm, username: event.target.value })} placeholder="chanda" /></label>
            <label className="form-field"><span>Email</span><input type="email" value={cashierForm.email} onChange={(event) => setCashierForm({ ...cashierForm, email: event.target.value })} placeholder="chanda@example.com" /></label>
            <label className="form-field"><span>Branch</span><select value={cashierForm.branch} onChange={(event) => setCashierForm({ ...cashierForm, branch: event.target.value })}><option value="">Select branch</option>{(branchesQuery.data || []).map((branch) => <option key={branch.id} value={branch.id}>{branch.name}</option>)}</select></label>
            <label className="form-field"><span>Login PIN</span><input type="password" inputMode="numeric" maxLength="8" value={cashierForm.pin} onChange={(event) => setCashierForm({ ...cashierForm, pin: event.target.value.replace(/\D/g, "") })} placeholder="4 to 8 digits" /></label>
          </div>
          <button className="button primary" disabled={createCashier.isPending || !cashierForm.full_name || !cashierForm.username || !cashierForm.email || !cashierForm.branch || cashierForm.pin.length < 4} onClick={() => createCashier.mutate({ ...cashierForm, client: clientQuery.data.id })}><UserPlus size={16} /> Add cashier</button>
          <div className="management-list">{(cashiersQuery.data || []).map((cashier) => <div className="management-list-row" key={cashier.id}><span><b>{cashier.full_name}</b><small>{cashier.username} · {cashier.branch_name || "Unassigned"}</small></span><span className={`status-badge ${!cashier.is_active ? "inactive" : ""}`}>{cashier.is_active ? "Active" : "Inactive"}</span></div>)}</div>
        </section>
      </div>
      <div className="panel management-note"><b>Administrator access</b><span>Use this area during client onboarding. Cashiers should only receive their own branch and PIN details.</span></div>
      <div className="settings-connection"><i /> API connection active · {cashierId || "cashier environment configured"}</div>
    </>
  );
}
function EmptyPage({ title }) {
  return (
    <div className="state-panel">
      <Archive size={26} />
      <h2>{title}</h2>
      <Link to="/" className="button primary">
        Back to dashboard
      </Link>
    </div>
  );
}

export default App;
