import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Database,
  LoaderCircle,
  Plus,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";

type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

type FormData = {
  name: string;
  email: string;
  password: string;
};

const initialForm: FormData = {
  name: "",
  email: "",
  password: "",
};

export default function App() {
  const [users, setUsers] = useState<User[]>([]);
  const [form, setForm] = useState<FormData>(initialForm);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [token, setToken] = useState<string | null>(null); 
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const loadUsers = useCallback(async (accessToken: string) => {
   try {
    const response = await fetch("/api/v1/users", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("No se pudieron cargar los usuarios");
    }

    const data: User[] = await response.json();
    setUsers(data);
    setError("");
  } catch (err) {
    setError(
      err instanceof Error ? err.message : "Error desconocido"
    );
  } finally {
    setLoading(false);
  }
}, []);

 useEffect(() => {
   if (token) {
     void loadUsers(token);
   } else {
     setUsers([]);
     setLoading(false);
   }
 }, [token, loadUsers]); 

  const filteredUsers = useMemo(() => {
    const term = search.toLowerCase().trim();

    return users.filter(
      (user) =>
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term)
    );
  }, [users, search]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (saving) return;

    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const response = await fetch("/api/v1/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("Este correo ya está registrado");
        }

        throw new Error("No fue posible registrar el usuario");
      }

      setForm(initialForm);
      setSuccess("Usuario registrado correctamente");
      if (!token) {
        throw new Error("Tu sesión ha expirado. Inicia sesión nuevamente.");
          }
      
      await loadUsers(token);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error desconocido"
      );
    } finally {
      setSaving(false);
    }
  }
  
  async function handleLogin(
    event: React.FormEvent<HTMLFormElement>
) {
    event.preventDefault();
    setAuthLoading(true);
    setError("");

    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
        }),
      });

      if (!response.ok) {
        throw new Error("Correo o contraseña incorrectos");
      }

      const data: {
        access_token: string;
        token_type: string;
      } = await response.json();

      setToken(data.access_token);
      setLoginPassword("");
      setLoading(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error de autenticación"
      );
    } finally {
      setAuthLoading(false);
    }
  }
 if (!token) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-blue-400">
            UserHub
          </h1>
          <p className="mt-2 text-slate-400">
            Inicia sesión para administrar usuarios
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label htmlFor="login-email" className="mb-2 block text-sm">
              Correo electrónico
            </label>
            <input
              id="login-email"
              type="email"
              required
              autoComplete="username"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="mb-2 block text-sm">
              Contraseña
            </label>
            <input
              id="login-password"
              type="password"
              required
              autoComplete="current-password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-400">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={authLoading}
            className="w-full rounded-lg bg-blue-600 p-3 font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {authLoading ? "Ingresando..." : "Iniciar sesión"}
          </button>
        </form>
      </div>
    </div>
  );
}  
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/70">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-2.5">
              <Users size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold">UserHub</h1>
              <p className="text-xs text-slate-400">
                User Management Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setToken(null);
                setUsers([]);
                setError("");
                setSuccess("");
              }}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
            >
              Cerrar sesión
            </button>
          <span className="flex items-center gap-2 rounded-full border border-emerald-800 bg-emerald-950 px-3 py-1 text-xs text-emerald-300">
            <Activity size={14} />
            Demo local
          </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-10">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Dashboard
          </h2>
          <p className="mt-2 text-slate-400">
            Administra los usuarios registrados en el sistema.
          </p>
        </div>

        <section className="grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Usuarios cargados",
              value: users.length,
              icon: Users,
            },
            {
              title: "Resultados de búsqueda",
              value: filteredUsers.length,
              icon: Search,
            },
            {
              title: "Infraestructura",
              value: "Docker",
              icon: Database,
            },
          ].map((stat) => (
            <div
              key={stat.title}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">
                  {stat.title}
                </span>
                <stat.icon className="text-blue-400" size={21} />
              </div>
              <p className="mt-4 text-3xl font-bold">{stat.value}</p>
            </div>
          ))}
        </section>

        <div className="grid items-start gap-6 lg:grid-cols-[380px_1fr]">
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-6 flex items-center gap-3">
              <Plus className="text-blue-400" />
              <h3 className="text-lg font-semibold">
                Registrar usuario
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  htmlFor="name"
                  className="mb-2 block text-sm text-slate-300"
                >
                  Nombre completo
                </label>
                <input
                  id="name"
                  required
                  minLength={2}
                  maxLength={100}
                  value={form.name}
                  onChange={(event) =>
                    setForm({ ...form, name: event.target.value })
                  }
                  placeholder="Ej. Ana García"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm text-slate-300"
                >
                  Correo electrónico
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(event) =>
                    setForm({ ...form, email: event.target.value })
                  }
                  placeholder="usuario@ejemplo.com"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm text-slate-300"
                >
                  Contraseña
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  maxLength={128}
                  autoComplete="new-password"
                  value={form.password}
                  onChange={(event) =>
                    setForm({ ...form, password: event.target.value })
                  }
                  placeholder="Mínimo 8 caracteres"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

              {error && (
                <p role="alert" className="text-sm text-red-400">
                  {error}
                </p>
              )}

              {success && (
                <p
                  role="status"
                  className="flex items-center gap-2 text-sm text-emerald-400"
                >
                  <CheckCircle2 size={16} />
                  {success}
                </p>
              )}

              <button
                type="submit"
                disabled={saving}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-3 font-semibold transition hover:bg-blue-500 disabled:opacity-50"
              >
                {saving ? (
                  <LoaderCircle className="animate-spin" size={18} />
                ) : (
                  <Plus size={18} />
                )}
                {saving ? "Registrando..." : "Registrar usuario"}
              </button>
            </form>

            <div className="mt-6 flex items-center gap-2 text-xs text-slate-400">
              <ShieldCheck size={16} className="text-emerald-400" />
              Contraseñas protegidas con Argon2
            </div>
          </section>

          <section className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
            <div className="flex flex-col justify-between gap-4 border-b border-slate-800 p-6 sm:flex-row sm:items-center">
              <div>
                <h3 className="text-lg font-semibold">
                  Usuarios registrados
                </h3>
                <p className="text-sm text-slate-400">
                  Listado de los últimos 100 usuarios
                </p>
              </div>

              <div className="relative">
                <Search
                  size={17}
                  className="absolute left-3 top-3 text-slate-500"
                />
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Buscar usuario..."
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950/70 text-slate-400">
                  <tr>
                    <th className="px-6 py-4">Nombre</th>
                    <th className="px-6 py-4">Correo</th>
                    <th className="px-6 py-4">Registro</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={3} className="px-6 py-10 text-center">
                        Cargando usuarios...
                      </td>
                    </tr>
                  ) : filteredUsers.length === 0 ? (
                    <tr>
                      <td
                        colSpan={3}
                        className="px-6 py-10 text-center text-slate-400"
                      >
                        No se encontraron usuarios.
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map((user) => (
                      <tr
                        key={user.id}
                        className="border-t border-slate-800 hover:bg-slate-800/50"
                      >
                        <td className="px-6 py-4 font-medium">
                          {user.name}
                        </td>
                        <td className="px-6 py-4 text-slate-400">
                          {user.email}
                        </td>
                        <td className="px-6 py-4 text-slate-400">
                          {new Date(user.created_at).toLocaleDateString(
                            "es-MX"
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-6 text-xs text-slate-500">
          <span>UserHub © 2026</span>
          <span>React · FastAPI · PostgreSQL · Redis · Docker</span>
        </footer>
      </main>
    </div>
  );
}
