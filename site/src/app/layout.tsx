import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { PROJECT } from "@/config/site";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "latin-ext"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: `${PROJECT.name} — ${PROJECT.tagline}`,
  description: PROJECT.description,
  openGraph: {
    title: `${PROJECT.name} — ${PROJECT.tagline}`,
    description: PROJECT.description,
    type: "website",
    locale: "pl_PL",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pl"
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
