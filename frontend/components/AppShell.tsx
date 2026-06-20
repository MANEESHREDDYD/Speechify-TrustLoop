"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, BookOpen, BrainCircuit, FlaskConical, Home, ShieldCheck } from "lucide-react";

const links = [
  { href: "/", label: "Overview", icon: Home },
  { href: "/library", label: "Library", icon: BookOpen },
  { href: "/demo", label: "Guided demo", icon: FlaskConical },
  { href: "/learning", label: "Learning", icon: BrainCircuit },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brand-mark"><ShieldCheck size={20} /></span>
          <span><b>S TrustLoop</b><small>Independent prototype</small></span>
        </Link>
        <nav>
          {links.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} className={pathname === href || (href !== "/" && pathname.startsWith(href)) ? "active" : ""}>
              <Icon size={18} /> {label}
            </Link>
          ))}
        </nav>
        <div className="local-pill"><span /> Local-first prototype</div>
        <p className="sidebar-note">Independent lexical-review research. No paid APIs or cloud dependency.</p>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
