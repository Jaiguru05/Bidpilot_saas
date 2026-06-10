"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { tokenStore } from "@/lib/api/client";

const navItems = [
  { href: "/dashboard", label: "Tenders", icon: "📄" },
  { href: "/dashboard/upload", label: "Upload", icon: "⬆️" },
  { href: "/dashboard/company", label: "Company Profile", icon: "🏢" },
  { href: "/dashboard/billing", label: "Billing", icon: "💳" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!tokenStore.access) router.push("/auth/login");
  }, [router]);

  const logout = () => {
    tokenStore.clear();
    router.push("/auth/login");
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="px-6 py-5 border-b">
          <div className="text-xl font-bold text-brand-600">BidPilot AI</div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  active
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t">
          <button
            onClick={logout}
            className="w-full px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg text-left"
          >
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
