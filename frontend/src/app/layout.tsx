import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Playfair_Display } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  weight: ["700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DineAI — Restaurant Recommender",
  description: "AI-powered restaurant picks from 51K+ Zomato venues",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`h-full overflow-hidden ${jakarta.variable} ${playfair.variable}`}
    >
      <body className="h-full overflow-hidden font-sans">{children}</body>
    </html>
  );
}
