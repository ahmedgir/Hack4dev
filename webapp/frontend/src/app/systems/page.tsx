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
  const analysedSystems = systems.filter((system) => system.sessions.length > 0);
  const awaitingSystems = systems.filter((system) => system.sessions.length === 0);

  return (
    <main>
      <SiteHeader />
      <section className="page-hero systems-hero">
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / TARGET SYSTEMS</p>
          <p className="eyebrow">ONE PROMISING RECOVERY · FOUR NON-CONFIRMING RESULTS</p>
          <h1>Evidence first. Targets second.</h1>
          <p>All eight planets were already confirmed by published astronomy. Our own observations currently support one promising preliminary recovery: CoRoT-2 b.</p>
        </div>
      </section>

      <section className="catalog-shell">
        <div className="catalog-intro">
          <div><p className="section-label">REVIEWED EVIDENCE</p><h2>Five systems entered the pipeline. One produced a promising recovery.</h2></div>
          <p>The other results are not “almost confirmed.” They are retained as transparent examples of incomplete coverage, excessive noise, or parameters that disagree with published values.</p>
        </div>
        <div className="system-grid">
          {analysedSystems.map((system) => {
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
        <section className="awaiting-catalog">
          <div className="awaiting-heading"><p className="section-label">AWAITING ANALYSIS</p><h2>Configured targets without a reviewed result.</h2><p>Illustrations provide visual context only. They are kept separate from observational evidence until a session completes the scientific pipeline.</p></div>
          <div className="awaiting-grid">
            {awaitingSystems.map((system) => (
              <article className="awaiting-card" key={system.slug}>
                <div className="awaiting-image"><img src={system.catalogImagePath} alt={system.imageLabel} /><span>{imageType[system.imageKind]}</span></div>
                <div className="awaiting-card-copy">
                  <p>{system.discoverySurvey}</p><h3>{system.planetName}</h3>{system.alias && <small>Also cataloged as {system.alias}</small>}
                  <dl><div><dt>Period</dt><dd>{system.periodDays} d</dd></div><div><dt>Published depth</dt><dd>{system.publishedDepthPercent}%</dd></div></dl>
                  <p className="image-caption">{system.imageLabel}</p>
                  <Link className="text-link" href={`/systems/${system.slug}`}>View target record</Link>
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
      <SiteFooter />
    </main>
  );
}
