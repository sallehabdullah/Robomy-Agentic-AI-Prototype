# Adipven.com — Site Crawl Index

**Source:** https://adipven.com (crawled via `wp-sitemap-*.xml` index + primary navigation menu)
**Extracted:** 2026-08-07
**Scope note:** Per instruction, the News section and all of its individual articles are excluded entirely from this index's "included" set and from downstream extraction. They are listed here only for completeness/audit purposes, under "Excluded — News".

## Included pages (substantive, non-News) — passed to extraction framework

### Core / Company
| Page | URL |
|---|---|
| Home | https://adipven.com/ |
| About Us | https://adipven.com/about-us/ |
| Services (overview) | https://adipven.com/services/ |
| Contacts | https://adipven.com/contacts/ |
| Photos (gallery, titles only) | https://adipven.com/photos/ |
| Appointment / Free Case Evaluation | https://adipven.com/appointment/ |

### Services (Tier 1/2 detail pages, from Services nav dropdown)
| Page | URL |
|---|---|
| Patents | https://adipven.com/patents-2/ |
| Trademarks | https://adipven.com/patents/ |
| Industrial Design | https://adipven.com/industrial_design/ |
| Copyrights | https://adipven.com/copyrights/ |
| Geographical Indications | https://adipven.com/geographical-indications-2/ |
| Licensing and Transfer of IP Ownership | https://adipven.com/licensing/ |
| IP Trainings and Talks | https://adipven.com/patents-3/ |
| IP Audit and IP Valuation | https://adipven.com/ip-audit-and-ip-valuation/ |
| Enforcement | https://adipven.com/enforcement-2/ |

### People / Team
| Page | URL |
|---|---|
| Practitioners (team overview page) | https://adipven.com/practitioners/ |
| Ramakrishna Damodharan | https://adipven.com/lawyer/ramakrishna-damodharan/ |
| Moganah Raman | https://adipven.com/lawyer/moganah-raman/ |
| Norlela Mat Lias | https://adipven.com/lawyer/norlela-mat-lias/ |
| Mohd Faizul Mohd Yin | https://adipven.com/lawyer/mohd-faizul-mohd-yin/ |
| Tharshini Maran | https://adipven.com/lawyer/tharshini-maran/ |
| Nur Amalina Zamani | https://adipven.com/lawyer/nur-amalina-zamani/ |
| Surain Satgunarajah | https://adipven.com/lawyer/surain-satgunarajah/ |
| Dr. Soon Wei Chook | https://adipven.com/lawyer/dr-soon-wei-chook/ |
| Mythili Thirunavukarasu | https://adipven.com/lawyer/mythili-thirunavukarasu/ |

### Case Studies / Portfolio (custom post type `case`, distinct from News post type)
34 items — legal case summaries and firm-announcement items published as a separate "portfolio" content type. Full URL list:
```
https://adipven.com/case/malaysia-ykl-engineering-defeated-during-appeal/
https://adipven.com/case/malaysia-patent-ultimate-decision-on-dependent-claims-survival-in-court/
https://adipven.com/case/malaysia-how-patent-damages-are-accessed-by-court/
https://adipven.com/case/malaysia-merck-sharp-dohme-hits-another-obstacle/
https://adipven.com/case/malaysia-kingtime-is-victorious/
https://adipven.com/case/malaysia-patent-found-to-invalid/
https://adipven.com/case/pph-myipo-cnipa/
https://adipven.com/case/cambodia-european-patents-can-now-be-validated-in-cambodia/
https://adipven.com/case/india-requirements-of-working-statements/
https://adipven.com/case/malaysia-court-of-appeal-held-skyworld-mark-is-well-known/
https://adipven.com/case/malaysia-a-decision-on-relevance-and-cause-of-action-relating-to-property-managers/
https://adipven.com/case/malaysia-trademark-infringement-and-obligation-of-online-platform-providers-defined-by-court/
https://adipven.com/case/malaysia-traders-can-be-found-liable-for-the-tort-of-passing-off/
https://adipven.com/case/malaysia-understanding-the-value-of-trademarks-co-existence-in-other-jurisdictions/
https://adipven.com/case/malaysia-effect-of-disclaimers-in-the-scope-of-trademark/
https://adipven.com/case/malaysia-biscuits-battle-in-court/
https://adipven.com/case/malaysia-jllp-appeals-allowed/
https://adipven.com/case/malaysia-passing-off-much/
https://adipven.com/case/sst-announcements/
https://adipven.com/case/iso-9001-2015-registration-announcement/
https://adipven.com/case/adipven-new-website-launched/
https://adipven.com/case/asean-trade-mark-intensive-industries-and-their-economic-contribution/
https://adipven.com/case/adipven-is-expanding/
https://adipven.com/case/new-year-wishes-from-the-managing-director/
https://adipven.com/case/our-patent-attorney-aisyah-won-the-best-paper-award/
https://adipven.com/case/asia-ip-pph-story/
https://adipven.com/case/women-scientists-in-patenting-bring-double-the-experience-to-the-table/
https://adipven.com/case/malaysia-estoppel-and-breach-of-contract/
https://adipven.com/case/malaysia-who-owns-the-bike/
https://adipven.com/case/malaysia-mirror-mirror-on-the-wall-whos-the-fairest-of-em-all/
https://adipven.com/case/malaysia-man-accused-of-malicious-cyber-attack-against-own-company-released-and-acquitted/
https://adipven.com/case/malaysia-jurisdiction-of-court-is-defined/
https://adipven.com/case/copyright-article-telekung/
https://adipven.com/case/malaysia-famous-filmmaker-co-continue-the-fight/
https://adipven.com/case/malaysia-a-copyright-saga/
```

## Excluded — News (per explicit instruction: disregard entirely)

- https://adipven.com/news/ and https://adipven.com/news-2/ — News landing/archive pages
- Approximately 250 individual News articles under the WordPress "post" post type (URL pattern `https://adipven.com/YYYY/MM/DD/slug/`), enumerated by `https://adipven.com/wp-sitemap-posts-post-1.xml`. Not reproduced here since the entire section was excluded from scope per instruction; the sitemap URL is provided for audit/traceability only.

## Excluded — orphaned/demo/duplicate pages (not linked from live navigation; theme placeholders or stub duplicates)

| Page | URL | Reason excluded |
|---|---|---|
| Sample Page | https://adipven.com/sample-page/ | Default WordPress placeholder text, not real content |
| Sample Page 2 | https://adipven.com/sample-page-2/ | Default WordPress placeholder, not linked in nav |
| Typography | https://adipven.com/typography/ | Theme demo/style-guide page |
| Homepage (draft variant) | https://adipven.com/homepage/ | Unused theme demo homepage variant, not linked in nav |
| Homepage 3 | https://adipven.com/homepage-3/ | Unused theme demo homepage variant |
| Homepage 5 | https://adipven.com/homepage-5/ | Unused theme demo homepage variant |
| Landing | https://adipven.com/landing/ | Unused theme demo landing page |
| Practices | https://adipven.com/practices/ | Generic law-firm theme template duplicating /services/; contains unverified stats ("100+ lawyers, 50+ countries, 40+ offices") inconsistent with the rest of the site and not corroborated elsewhere — treated as leftover theme demo content, not genuine Adipven content |
| Ramakrishna Damodharan (stub) | https://adipven.com/ramakrishna-damodharan/ | Empty stub duplicate of the canonical profile at /lawyer/ramakrishna-damodharan/; contains no biographical content |
| Team archive index | https://adipven.com/lawyer/ | Pure auto-generated listing (photos/titles only), fully duplicated by the individual profile pages and the Practitioners page |
| Videos | https://adipven.com/videos/ | No actual video content, descriptions, or media present — page is navigation/chatbot/cookie boilerplate only |

## Method

1. Retrieved `https://adipven.com/sitemap.xml` (WordPress sitemap index) and its child sitemaps: `wp-sitemap-posts-post-1.xml` (News/blog posts), `wp-sitemap-posts-page-1.xml` (static pages), `wp-sitemap-posts-team-1.xml` (team/lawyer profiles), `wp-sitemap-posts-portfolio-1.xml` (case studies).
2. Retrieved the homepage's rendered navigation (header menu + footer) to identify the live, user-facing site structure and cross-check which sitemap pages are actually linked vs. orphaned.
3. Spot-fetched ambiguous/unlinked sitemap pages individually to determine whether each was genuine content or a leftover theme/demo page.
