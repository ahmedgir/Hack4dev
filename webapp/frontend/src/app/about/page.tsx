import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "About",
  description: "The purpose, evidence policy, and present scope of the Hack4Dev Exoplanet Data Portal.",
};

export default function AboutPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero">
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / ABOUT</p>
          <p className="eyebrow">HACK4DEV IRAQ 2026</p>
          <h1>Built to make the evidence understandable.</h1>
          <p>The Exoplanet Data Portal turns a real photometry pipeline into a public, inspectable experience without overstating the science.</p>
        </div>
      </section>

      <section className="content-shell about-grid">
        <article>
          <p className="section-label">THE PROJECT</p>
          <h2>A bridge between raw astronomy data and human judgment.</h2>
          <p className="lead">FITS files are rich in evidence, but difficult to interpret without specialist software. Our goal is to preserve that evidence while making the path to a conclusion visible.</p>
          <p>The scientific pipeline performs calibration, sky registration, differential photometry, quality control, and model comparison. This website exposes the outputs as an explorable record rather than presenting a single polished chart without context.</p>
        </article>
        <aside className="principles-card">
          <p className="section-label">EVIDENCE POLICY</p>
          <ul>
            <li><strong>Real inputs</strong><span>Every displayed measurement comes from a telescope frame.</span></li>
            <li><strong>Traceable exclusions</strong><span>Rejected frames keep a recorded reason.</span></li>
            <li><strong>Published comparison</strong><span>Claims are tested against known orbital parameters.</span></li>
            <li><strong>Honest language</strong><span>A recovery is never labeled as a new discovery.</span></li>
          </ul>
        </aside>
      </section>

      <section className="scope-section">
        <p className="section-label">CURRENT SCOPE</p>
        <h2>One complete system now. A repeatable structure for the rest.</h2>
        <p>CoRoT-2 b is the first fully published case in the portal. Additional systems can be added through the same catalog structure as their pipeline products are completed and reviewed.</p>
        <div className="scope-links">
          <Link className="nasa-button" href="/explorer">Explore the first system <span aria-hidden="true">→</span></Link>
          <Link className="text-link" href="/methodology">Review the scientific stack</Link>
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
