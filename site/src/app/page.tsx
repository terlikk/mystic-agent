import { Navbar } from "@/components/site/navbar";
import { Hero } from "@/components/site/hero";
import { ContentTabs } from "@/components/site/tabs";
import { PillarsPanel } from "@/components/site/pillars";
import {
  CapabilitiesPanel,
  Footer,
  HowItWorksPanel,
  RoadmapPanel,
} from "@/components/site/sections";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <ContentTabs
          tabs={[
            { key: "filary", label: "Filary", content: <PillarsPanel /> },
            {
              key: "mozliwosci",
              label: "Możliwości",
              content: <CapabilitiesPanel />,
            },
            {
              key: "jak-dziala",
              label: "Jak działa",
              content: <HowItWorksPanel />,
            },
            { key: "roadmapa", label: "Roadmapa", content: <RoadmapPanel /> },
          ]}
        />
      </main>
      <Footer />
    </>
  );
}
