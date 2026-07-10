import { Navbar } from "@/components/site/navbar";
import { ScrollHero } from "@/components/site/scroll-hero";

export default function Home() {
  return (
    <div className="bg-[#04060a]">
      <Navbar />
      <main>
        <ScrollHero />
      </main>
    </div>
  );
}
