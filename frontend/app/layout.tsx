import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "S TrustLoop",
  description: "Independent local prototype for reviewing generated voice-first learning and work outputs against source text.",
  openGraph: {
    title: "S TrustLoop",
    description: "S TrustLoop is an independent local prototype for lexical source review.",
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
