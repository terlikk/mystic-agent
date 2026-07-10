import { Navbar } from "@/components/site/navbar";
import { Hero } from "@/components/site/hero";
import { Pillars } from "@/components/site/pillars";
import {
  Capabilities,
  Footer,
  HowItWorks,
  Roadmap,
} from "@/components/site/sections";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Pillars />
        <Capabilities />
        <HowItWorks />
        <Roadmap />
      </main>
      <Footer />
    </>
  );
}
