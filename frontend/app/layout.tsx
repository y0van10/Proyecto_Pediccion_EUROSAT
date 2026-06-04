import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "EuroSAT AI - Satellite Classification",
  description: "Professional Deep Learning Image Classification Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="light">
      <body className={`${inter.className} bg-background text-foreground min-h-screen antialiased selection:bg-blue-500/30`}>
        {/* Decorative Background Elements */}
        <div className="bg-mesh" />
        <div className="bg-blob top-[-10%] left-[-10%] bg-blue-600/20" />
        <div className="bg-blob bottom-[-10%] right-[-10%] bg-purple-600/20" />
        
        <main className="relative z-10 max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </main>
        <Toaster position="top-center" theme="system" richColors closeButton />
      </body>
    </html>
  );
}
