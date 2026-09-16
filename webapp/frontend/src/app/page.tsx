import { TransitExplorer } from "@/components/TransitExplorer";
import { featuredSystem } from "@/data/systems";

const session = featuredSystem.sessions[0];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <div className="masthead">
          <a className="portal-brand" href="#top" aria-label="الصفحة الرئيسية">
            <span className="portal-seal" aria-hidden="true">H4D</span>
            <span>
              <strong>Exoplanet Data Portal</strong>
              <small>Hack4Dev Iraq 2026</small>
            </span>
          </a>
          <nav className="primary-nav" aria-label="التنقل الرئيسي">
            <a href="#method">المنهجية</a>
            <a href="#explorer">استكشف البيانات</a>
            <a href="#verdict">النتائج</a>
            <a href="#about">عن المشروع</a>
          </nav>
          <span className="search-label" aria-hidden="true">⌕</span>
        </div>
        <nav className="section-nav" aria-label="أقسام أداة الاكتشاف">
          <strong>Transit Explorer</strong>
          <a href="#top">نظرة عامة</a>
          <a href="#method">كيف نحلل FITS؟</a>
          <a href="#explorer">CoRoT-2</a>
          <span>الأنظمة الأخرى — قريبًا</span>
        </nav>
      </header>

      <section className="hero" id="top">
        <img
          src="/media/systems/corot-2/2026-08-09/hero-field.png"
          alt="حقل نجمي حقيقي من جلسة رصد CoRoT-2"
        />
        <div className="hero-overlay" />
        <div className="hero-inner">
          <p className="breadcrumb" dir="ltr">HOME / DISCOVERY TOOL / TRANSIT EXPLORER</p>
          <div className="hero-copy">
            <p className="eyebrow" dir="ltr">REAL TELESCOPE DATA · 87 FITS FRAMES</p>
            <h1>Exoplanet<br />Transit Explorer</h1>
            <p>
              أداة تفاعلية تتبع ضوء نجم حقيقي عبر الزمن، وتوضح كيف يمكن لعبور كوكب معروف أن يترك انخفاضًا صغيرًا قابلًا للقياس.
            </p>
          </div>
        </div>
      </section>

      <section className="overview" id="about">
        <article className="overview-copy">
          <p className="section-label" dir="ltr">THE QUESTION</p>
          <h2>كيف نرى كوكبًا لا يظهر في الصورة؟</h2>
          <p className="lead">
            نحن لا نصور الكوكب نفسه. نحدد نجمه المضيف من إحداثياته السماوية، ثم نقيس سطوع النجم في عشرات الصور المتتابعة.
          </p>
          <p>
            عندما يعبر الكوكب أمام النجم ينخفض الضوء بنسبة صغيرة. نقارن هذا الانخفاض بنجوم مرجعية وبالتوقيت والعمق والمدة المنشورة، ثم نقرر إن كانت جلسة الرصد قوية بما يكفي أم لا.
          </p>
        </article>

        <aside className="featured-record">
          <p className="section-label" dir="ltr">FEATURED OBSERVATION</p>
          <h3 dir="ltr">CoRoT-2 b</h3>
          <p>{featuredSystem.shortDescriptionAr}</p>
          <dl>
            <div><dt>الدورة المدارية</dt><dd dir="ltr">{featuredSystem.periodDays.toFixed(2)} days</dd></div>
            <div><dt>عمق العبور المنشور</dt><dd dir="ltr">{featuredSystem.publishedDepthPercent}%</dd></div>
            <div><dt>الإطارات المقبولة</dt><dd dir="ltr">{session.acceptedFrames} / {session.totalFrames}</dd></div>
          </dl>
          <a href="#explorer" className="nasa-button">افتح جلسة الرصد <span aria-hidden="true">←</span></a>
        </aside>
      </section>

      <section className="method" id="method">
        <div className="method-heading">
          <p className="section-label" dir="ltr">FROM FITS TO EVIDENCE</p>
          <h2>أربع خطوات، وكل خطوة قابلة للفحص</h2>
        </div>
        <ol className="method-list">
          <li><span>01</span><div><h3>تحديد السماء</h3><p>يحوّل WCS إحداثيات RA/Dec إلى موضع دقيق داخل الصورة.</p></div></li>
          <li><span>02</span><div><h3>قياس الضوء</h3><p>نقيس ضوء الهدف بعد طرح الخلفية وضوضاء الحساس.</p></div></li>
          <li><span>03</span><div><h3>المقارنة</h3><p>نجوم Gaia المرجعية تزيل تغيرات الجو المشتركة في الحقل.</p></div></li>
          <li><span>04</span><div><h3>الحكم</h3><p>نقارن التغطية والدقة والعمق والمدة والتوقيت بالقيم المنشورة.</p></div></li>
        </ol>
      </section>

      <TransitExplorer session={session} />

      <section className="verdict" id="verdict">
        <div className="verdict-copy">
          <p className="section-label" dir="ltr">SCIENTIFIC RESULT</p>
          <h2>استعادة أولية واعدة لعبور معروف.</h2>
          <p>النتيجة متوافقة في العمق والتوقيت، لكنها ليست اكتشافًا جديدًا ولا تأكيدًا مستقلًا. هذا الفرق جزء من الأداة، لا ملاحظة مخفية.</p>
        </div>
        <div className="result-numbers" dir="ltr">
          <div><span>MEASURED DEPTH</span><strong>3.18%</strong></div>
          <div><span>PUBLISHED DEPTH</span><strong>2.75%</strong></div>
          <div><span>ACCEPTED FRAMES</span><strong>73 / 87</strong></div>
        </div>
      </section>

      <footer>
        <div className="footer-brand">
          <span className="portal-seal" aria-hidden="true">H4D</span>
          <div><strong>Exoplanet Data Portal</strong><small>Discovery Tool · Challenge E</small></div>
        </div>
        <p>بيانات حقيقية، أدلة قابلة للتتبع، وحدود علمية معلنة.</p>
      </footer>
    </main>
  );
}
