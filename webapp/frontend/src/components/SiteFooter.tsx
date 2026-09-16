import Link from "next/link";

export function SiteFooter() {
  return (
    <footer>
      <div className="footer-brand">
        <span className="portal-seal" aria-hidden="true">H4D</span>
        <div><strong>Exoplanet Data Portal</strong><small>Discovery Tool · Challenge E</small></div>
      </div>
      <nav className="footer-links" aria-label="Footer navigation">
        <Link href="/explorer">Explorer</Link>
        <Link href="/methodology">Methodology</Link>
        <Link href="/about">About</Link>
      </nav>
      <p>Real observations. Traceable evidence. Honest limits.</p>
    </footer>
  );
}
