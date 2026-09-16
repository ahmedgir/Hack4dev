import type { Metadata } from "next";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Sources and image credits",
  description: "Image provenance, scientific data sources, and reuse notes for the Exoplanet Data Portal.",
};

const sources = [
  {
    type: "SYSTEM-SPECIFIC ARTIST’S CONCEPT",
    title: "CoRoT-2 b artist’s concept",
    used: "CoRoT-2 b catalog card",
    credit: "NASA Science — Exoplanet Catalog",
    note: "An illustration of the system, not a telescope photograph. NASA is acknowledged; use does not imply NASA endorsement.",
    href: "https://science.nasa.gov/exoplanet-catalog/corot-2-b/",
  },
  {
    type: "REPRESENTATIVE ARTIST’S CONCEPT",
    title: "Hot-Jupiter concept",
    used: "TrES-1 b, TrES-5 b, and HAT-P-10 b placeholders",
    credit: "NASA Science — Exoplanet Exploration",
    note: "Used only where no project field is published. It represents the planet class and is explicitly not presented as an image of those individual planets.",
    href: "https://science.nasa.gov/exoplanets/gas-giant/",
  },
  {
    type: "PROCESSED OBSERVATION",
    title: "Verified stellar-field figures",
    used: "WASP-10 b, WASP-2 b, Qatar-1 b, and TrES-3 b catalog cards",
    credit: "Hack4Dev processing of MicroObservatory FITS observations",
    note: "The figures mark the host star in real telescope frames. The exoplanet itself is not spatially visible in these images.",
    href: "https://mo-www.cfa.harvard.edu/MicroObservatory/index.html",
  },
  {
    type: "SCIENTIFIC PARAMETERS",
    title: "Orbital period, transit depth, duration, and coordinates",
    used: "All target cards and pipeline configuration",
    credit: "NASA Exoplanet Archive and NASA Exoplanet Catalog",
    note: "Published reference values are kept separate from our measured results and analysis labels.",
    href: "https://exoplanetarchive.ipac.caltech.edu/",
  },
];

export default function SourcesPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero">
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / SOURCES</p>
          <p className="eyebrow">PROVENANCE · CREDIT · CONTEXT</p>
          <h1>Images should clarify the evidence—not imitate it.</h1>
          <p>This record states where each visual came from, what it depicts, and where an image is illustrative rather than observational.</p>
        </div>
      </section>

      <section className="sources-shell">
        <div className="sources-intro">
          <p className="section-label">SOURCE REGISTER</p>
          <h2>Trace every visual back to its origin.</h2>
        </div>
        <div className="source-list">
          {sources.map((source, index) => (
            <article className="source-record" key={source.title}>
              <span className="source-number">{String(index + 1).padStart(2, "0")}</span>
              <div><p className="source-type">{source.type}</p><h2>{source.title}</h2><p>{source.note}</p></div>
              <dl><div><dt>Used for</dt><dd>{source.used}</dd></div><div><dt>Credit</dt><dd>{source.credit}</dd></div></dl>
              <a className="nasa-button" href={source.href} target="_blank" rel="noreferrer">Open original source <span aria-hidden="true">↗</span></a>
            </article>
          ))}
        </div>
      </section>

      <section className="reuse-note">
        <p className="section-label">REUSE NOTE</p>
        <h2>Credit is visible by design.</h2>
        <p>NASA imagery is used for educational and informational presentation with NASA identified as the source. Project-generated field figures remain tied to the observations and processing that produced them. No credit here implies endorsement by NASA, Harvard, or the Smithsonian.</p>
      </section>
      <SiteFooter />
    </main>
  );
}
