import type { Metadata } from "next";
import { Fraunces, Inter, JetBrains_Mono } from "next/font/google";
import { PROJECT } from "@/config/site";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "latin-ext"],
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://mystic-agent.vercel.app"),
  title: {
    default: `${PROJECT.name} — otwarty, self-hosted agent AI (Twój Jarvis)`,
    template: `%s · ${PROJECT.name}`,
  },
  description:
    "MysticAgent to open-source'owy, self-hosted agent AI, który mieszka na Twoim komputerze. Ogarnia pocztę i kalendarz, umawia wizyty i rezerwacje, dzwoni w Twoim imieniu, robi research — a o ważne rzeczy pyta Ciebie. Zero chmury, zero kont.",
  keywords: [
    "mystic agent",
    "mysticagent",
    "agent AI",
    "self-hosted AI agent",
    "open source Jarvis",
    "osobisty asystent AI",
    "autonomiczny agent AI",
    "agent AI po polsku",
    "AI który umawia wizyty",
    "AI asystent telefoniczny",
  ],
  alternates: { canonical: "/" },
  robots: { index: true, follow: true },
  authors: [{ name: "Filip Terlikowski" }],
  openGraph: {
    title: `${PROJECT.name} — otwarty, self-hosted agent AI`,
    description: PROJECT.description,
    url: "https://mystic-agent.vercel.app",
    siteName: PROJECT.name,
    type: "website",
    locale: "pl_PL",
  },
  twitter: {
    card: "summary_large_image",
    title: `${PROJECT.name} — otwarty, self-hosted agent AI`,
    description: PROJECT.description,
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
      className={`dark ${inter.variable} ${fraunces.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col overflow-x-hidden bg-[#08080f]">
        {children}
      </body>
    </html>
  );
}
