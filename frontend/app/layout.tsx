import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "S TrustLoop",
  description: "Independent AI reliability engine for voice-first learning, meetings, podcasts, and work agents.",
  openGraph: {
    title: "S TrustLoop",
    description: "S TrustLoop is an independent prototype for voice-first AI reliability.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><AppShell>{children}</AppShell></body>
    </html>
  );
}
