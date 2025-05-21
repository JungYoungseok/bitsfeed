
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import DatadogRUMWrapper from "@/components/DatadogRUMWrapper";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Bitsfeed",
  description: "Stay updated on all things Datadog.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <DatadogRUMWrapper /> {/* ✅ 실제 실행 */}
        {children}
      </body>
    </html>
  );
}
