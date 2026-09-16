import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="masthead">
        <Link className="portal-brand" href="/" aria-label="Exoplanet Data Portal home">
          <span className="portal-seal" aria-hidden="true">H4D</span>
          <span>
            <strong>Exoplanet Data Portal</strong>
            <small>Hack4Dev Iraq 2026</small>
          </span>
        </Link>
        <nav className="primary-nav" aria-label="Primary navigation">
          <Link href="/">Overview</Link>
          <Link href="/systems">Systems</Link>
          <Link href="/systems/corot-2">Explore data</Link>
          <Link href="/methodology">Methodology</Link>
          <Link href="/about">About</Link>
        </nav>
        <span className="search-label" aria-hidden="true">⌕</span>
      </div>
      <nav className="section-nav" aria-label="Portal sections">
        <strong>Transit Explorer</strong>
        <Link href="/systems">Target catalog</Link>
        <Link href="/methodology">From FITS to evidence</Link>
        <Link href="/systems/corot-2">CoRoT-2 b</Link>
        <Link href="/sources">Sources &amp; credits</Link>
      </nav>
    </header>
  );
}
