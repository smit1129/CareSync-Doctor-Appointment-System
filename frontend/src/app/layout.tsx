import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";
import Link from "next/link";
import { Logo } from "@/components/Logo";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CareSync — Connect. Book. Care.",
  description: "Professional healthcare appointment booking platform. Search doctors by specialization, book appointments, manage your health journey seamlessly.",
  keywords: "doctor appointment, healthcare, booking, medical, consultation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <AuthProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <footer className="bg-gray-900 text-gray-400 py-8 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Logo />
                  </h3>
                  <p className="text-sm">CareSync: Connect. Book. Care. Connecting patients with the best doctors.</p>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-3">Quick Links</h4>
                  <ul className="space-y-2 text-sm">
                    <li><Link href="/doctors" className="hover:text-teal-400 transition-colors">Find Doctors</Link></li>
                    <li><Link href="/auth/register" className="hover:text-teal-400 transition-colors">Patient Registration</Link></li>
                    <li><Link href="/auth/login" className="hover:text-teal-400 transition-colors">Login</Link></li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-3">CareSync Support</h4>
                  <ul className="space-y-2 text-sm">
                    <li>📧 support@caresync.local</li>
                    <li>🏥 Doctor Appointment Management System</li>
                    <li>📋 Software Engineering Lab Project</li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-gray-800 mt-8 pt-6 text-center text-sm">
                © 2026 CareSync — Connect. Book. Care. | Developed by Smit & Rohit
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
