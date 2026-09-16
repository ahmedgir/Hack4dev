import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { getSystemStatus, statusLabels, systems } from "@/data/systems";

export const metadata: Metadata = {
  title: "Target systems",
  description: "The Hack4Dev target catalog, current analysis status, telescope fields, and published parameters.",
};

const imageType = {
  artist_concept: "ARTIST’S CONCEPT",
  verified_field: "PROCESSED TELESCOPE FIELD",
  representative_concept: "REPRESENTATIVE CONCEPT",
};

const statusTone = {
  promising_preliminary_transit: "promising",
  insufficient_for_transit_claim: "insufficient",
  transit_like_but_parameters_inconsistent: "inconsistent",
  not_analysed: "not_analysed",
};

export default function SystemsPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero systems-hero">
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / TARGET SYSTEMS</p>
          <p className="eyebrow">EIGHT TARGETS · VISIBLE STATUS</p>
          <h1>The catalog, including what is not ready.</h1>
          <p>Each card separates published system parameters from our own analysis status. Illustrations are labeled; telescope fields show the host star, not the planet itself.</p>
        </div>
      </section>

      <section className="catalog-shell">
        <div className="catalog-intro">
          <div><p className="section-label">TARGET CATALOG</p><h2>Known planets. Independently inspected observations.</h2></div>
          <p>Only CoRoT-2 b currently has a promising preliminary recovery. Incomplete and unanalysed targets remain visible so the portal never turns missing evidence into a success.</p>
        </div>
        <div className="system-grid">
          {systems.map((system) => {
            const status = getSystemStatus(system);
            return (
            <article className="system-card" key={system.slug}>
              <div className="system-image">
                <img src={system.catalogImagePath} alt={system.imageLabel} />
                <span>{imageType[system.imageKind]}</span>
              </div>
              <div className="system-card-body">
                <div className="system-card-heading">
                  <div><p>{system.discoverySurvey}</p><h2>{system.planetName}</h2>{system.alias && <small>Also cataloged as {system.alias}</small>}</div>
                  <span className={`catalog-status ${statusTone[status]}`}>{statusLabels[status]}</span>
                </div>
                <p className="system-summary">{system.shortDescription}</p>
                <dl className="system-facts">
                  <div><dt>Period</dt><dd>{system.periodDays} d</dd></div>
                  <div><dt>Published depth</dt><dd>{system.publishedDepthPercent}%</dd></div>
                  <div><dt>Duration</dt><dd>{system.durationHours} h</dd></div>
                  <div><dt>Reviewed sessions</dt><dd>{system.sessions.length}</dd></div>
                  <div><dt>RA</dt><dd>{system.raDeg.toFixed(6)}°</dd></div>
                  <div><dt>Dec</dt><dd>{system.decDeg.toFixed(6)}°</dd></div>
                </dl>
                <p className="image-caption">{system.imageLabel}</p>
                <div className="card-actions">
                  <Link className="text-link" href={`/systems/${system.slug}`}>{system.sessions.length ? "Open evidence" : "View target"}</Link>
                  <a className="source-link" href={system.sourceUrl} target="_blank" rel="noreferrer">NASA catalog source ↗</a>
                </div>
              </div>
            </article>
          );})}
        </div>
      </section>
      <section className="page-cta source-cta">
        <div><p className="section-label">IMAGE PROVENANCE</p><h2>Every visual has a traceable origin.</h2></div>
        <Link className="nasa-button" href="/sources">Review image sources <span aria-hidden="true">→</span></Link>
      </section>
      <SiteFooter />
    </main>
  );
}
