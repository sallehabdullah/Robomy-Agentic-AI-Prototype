# Adipven — Content Store

**Source:** https://adipven.com (live site, WordPress sitemaps + navigation crawl)
**Extracted:** 2026-08-07
**Coverage note:** Covers all substantive non-News content on adipven.com: 9 IP service pages, the Services overview page, 8 team/lawyer profile pages plus the Practitioners overview page, Home, About Us, Contacts, Photos, Appointment, and 35 entries from the site's "Case Studies" (portfolio) content type. The News section (~250 blog-post articles under `/YYYY/MM/DD/slug/`, plus the `/news/` and `/news-2/` landing pages) was excluded entirely per explicit instruction and is not represented below except as a line item in the companion crawl index (`00-index.md`). A handful of orphaned WordPress theme/demo pages not linked from live navigation (sample-page, typography, homepage-3/5, landing, practices, a duplicate stub lawyer page) were also excluded — see `00-index.md` for the full list and reasoning.

---

## Contact & Identifying Information

**Company registration (source: Contacts page):** "ADIPVEN (M) SDN. BHD. (968005-T / 201101039883)"

**Headquarters address (source: Contacts page, verbatim):** "A-16-5 & A-16-6 Menara UOA Bangsar No. 5, Jalan Bangsar Utama 1 59000 Kuala Lumpur Malaysia"

A separate firm announcement (source: Case Studies — "Adipven is Expanding," dated by internal reference to 3 April 2017) gives a slightly different, later HQ suite listing: "A-16-5, A-16-6 & A-33-3A, Menara UOA Bangsar, No. 5, Jalan Bangsar Utama 1, 59000 Kuala Lumpur, Malaysia" — i.e. an additional suite "A-33-3A" not present on the current Contacts page. `[CONFLICTING: current Contacts page lists suites A-16-5 & A-16-6 only; a 2017-dated firm announcement lists A-16-5, A-16-6 & A-33-3A]` This may simply reflect a since-vacated expansion suite; not resolved from source material.

**Branch office address (source: Contacts page, verbatim):** "Unit 02-02, Level 2, CIMB Leadership Academy, No.3, Jalan Medini Utara 1, Medini Iskandar, 79200 Iskandar Puteri, Johor Darul Takzim Malaysia"

**Phone (source: Contacts page):** "+603 2201 4023 / +603 2201 4026"

**Fax (source: Contacts page):** "+603 2201 4025"

**Primary email (source: Contacts page, and repeated as sign-off contact on multiple firm announcements in Case Studies):** "info@adipven.com"

**Website (source: Contacts page):** "www.adipven.com"

`[CONFLICTING: reason]` — A second email domain, "info@adipven.edu.my", appears on the Home page within Terms & Conditions/data-privacy boilerplate text (not the primary contact section). This conflicts with the Contacts-page email. The Contacts-page value ("info@adipven.com") is treated as authoritative since it appears in dedicated contact content and is also the email given as sign-off on multiple firm announcements (SST Announcements, ISO 9001 Registration Announcement, Adipven New Website Launched), while "info@adipven.edu.my" appears only once, in legal boilerplate.

No phone or fax number was found as plain text on the Home page; confirmed only on the Contacts page.

Additional contact channels noted on the Contacts page: a WhatsApp link (formatted as an API link, destination not resolvable from fetched content) and a website contact form. A chatbot widget ("Frank") is present site-wide; its UI text is excluded as non-substantive per extraction rules.

---

## Services / Products

### Services (Overview)
**Source:** https://adipven.com/services/

Page heading: "ADIPVEN™" followed by a section heading "Services".

Body text (verbatim): "From its headquarters in KL, ADIPVEN™ acts as a one-stop IP and commercialization centre to coordinate all our clients IP and commercialization matters in Asia, particularly in Malaysia, India, Singapore, Vietnam, Indonesia, Thailand, The Philippines etc. As an Asian Intellectual Property Partner."

Body text (verbatim, second paragraph): "ADIPVEN™ provides a total IP and commercialization solution from a single contact point. If you have an enquiry on IP and commercialization in any Asian countries, all you need to do is to write to us instead of contacting all your associates and agents in those countries."

The page contains a "Find Out More" link whose destination could not be resolved from fetched content.

`[UNCERTAIN: reason]` — repeated fetches of this page were inconsistent about whether it also displays a list of nine named practitioners and a bullet list of the nine service-category names; one pass returned them, a verbatim-reproduction pass did not and described them as repeating navigation/widget structure. Not included as confirmed body content here. `[CONFLICTING: version A (names + category list present as body content) vs version B (verbatim pass — absent, described as nav/widget chrome)]`

### Patents
**Source:** https://adipven.com/patents-2/

Page heading: "Patents"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients in conducting novelty, infringement and landscape patent searches. ADIPVEN™ also assists in drafting and filing patent applications for our domestic and foreign clients throughout Asia. Our subject matter experts are experienced patent drafters with suitable technical backgrounds such as chemistry, mechanical engineering, electrical and electronic engineering, information and communication technology (ICT), biotechnology, microbiology etc. Although most Asian countries only provide standard patent protections, countries like Malaysia, Japan, China, Australia, Indonesia and Thailand provide a further protection in the form of utility innovation, utility model and petty patent system."

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

### Trademarks
**Source:** https://adipven.com/patents/ — note: despite the URL slug, this page's content is about Trademarks, not patents.

Page heading: "Trademarks"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients in conducting thorough trademark searches and advises clients on the best strategy in obtaining trademarks in Asia."

Body text (verbatim, continued): "Asia is the largest region in the world and with the largest population in the world. Asia is multi-ethic, multi-religious, multi-lingual and multi-cultural society. Although English in widely spoken in Asia, there are other local languages which are being widely used within the country such as Mandarin (in countries like China, Taiwan, Hong Kong, Malaysia and Singapore), Malay (Indonesia, Malaysia, Singapore and Brunei), Hindi, Tamil, Telugu, Malayalam (India and Sri Lanka), Urdu (India, Pakistan and Bangladesh) Arabic (Middle East), Tagalog (The Philippines), Thai (Thailand), Vietnamese (Vietnam), Cambodian (Cambodia) etc. Therefore, it is prudent to select trademarks with appropriate to language and alphabet. It is also important have the trademarks to be translated and transliterated into the local languages."

(The spelling "multi-ethic" and the grammar "Although English in widely spoken" / "It is also important have the trademarks" are reproduced exactly as they appear in the source — apparent source-site typos, not transcription errors.)

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

### Industrial Design
**Source:** https://adipven.com/industrial_design/

Page heading: "Industrial Designs"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients in conducting industrial design searches and file industrial design to applications."

Body text (verbatim, continued): "Industrial design refers features of shape, configuration, pattern or ornament applied on an article by any industrial process or means. In Asia, some countries follow multi-class applications whereas others follow single-class applications."

No pricing, fee schedule, further process-step detail, or named individual contact appears in the fetched content for this page.

### Copyrights
**Source:** https://adipven.com/copyrights/

Page heading: "Copyrights"

Body text (verbatim, confirmed consistent across two independent fetches): "Asia generally has developed copyright laws and most of them are members of the Berne Convention. In most Asian countries like Malaysia, Thailand and Singapore, there is no registration system for registering or depositing copyrighted materials. Therefore, ADIPVEN™ assists clients in preparing Statutory Declarations in affirming the ownership of the copyright materials.

However in countries like Indonesia and India, it is advisable to register the copyrighted materials with the Copyright Office and this enables the copyright owners to claim damages in court in the event that their copyright has been infringed by third parties.

ADIPVEN™ assists clients in registering copyrighted materials with the Copyright Office and assists in copyright infringement cases with our associate law firm."

The page states the firm works "with our associate law firm" on copyright infringement cases; the associate law firm is not named on this page.

No pricing, fee schedule, or named individual contact appears in the fetched content for this page.

### Geographical Indications
**Source:** https://adipven.com/geographical-indications-2/

Page heading: "Geographical Indications"

Body text (verbatim, first fetch): "Geographical Indications (GI) refer to a product which indicate its place or area of origin and possess certain qualities, enjoy certain reputation and other characteristics of the product due to its geographical origin." / "This is one of the new legislations and has been used extensively by clients particularly from the European regions." / "As a registered GI agent, ADIPVEN™ can assist clients in filing and prosecuting GI applications in Malaysia and abroad."

`[UNCERTAIN: reason]` — a second fetch returned the same substantive claims but paraphrased ("This represents a relatively new legislative area...", "As an authorized GI agent..."). The exact verbatim wording of the second and third sentences is not fully confirmed character-for-character; the first-fetch wording above (presented as direct quotation) is used as the primary record.

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

### Licensing And Transfer of IP Ownership
**Source:** https://adipven.com/licensing/

Page heading: "Licensing And Transfer of IP Ownership"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients in drafting license agreements and assignments. ADIPVEN™ also advises on corporate transactions such as mergers and acquisitions."

`[CONFLICTING: version A "advises of corporate transactions" vs version B "advises on corporate transactions"]` — one fetch rendered the second sentence with "advises of corporate transactions" [ILLEGIBLE: possible source typo], another with "advises on corporate transactions." "On" is used above as the more grammatically standard reading, but the source may read "of."

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

### IP Trainings And Talks
**Source:** https://adipven.com/patents-3/ — note: despite the URL slug, this page's content is about IP Trainings and Talks, not patents.

Page heading: "IP Trainings And Talks"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients in providing IP related trainings and talks to ensure that clients' management team, research and development team, managers and the entire clients' staff members understand and appreciate the use of IP rights as a main tool to grow."

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

`[UNCERTAIN: reason]` — one fetch pass appended unquoted claims ("falls under ADIPVEN's broader portfolio," "the firm's team of nine IP practitioners delivers these training programs") not presented as direct quotations and not corroborated by a verbatim-reproduction fetch. Excluded from confirmed body text above.

### IP Audit And IP Valuation
**Source:** https://adipven.com/ip-audit-and-ip-valuation/

Page heading: "IP Audit And IP Valuation"

Body text (verbatim, confirmed consistent across two independent fetches): "ADIPVEN™ assists clients conducting IP Audit to determine various IP rights that clients may have and in valuating clients' IP rights. Once identified, ADIPVEN™ assists clients in ensuring their IP rights are properly secured, managed and commercialized."

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

`[UNCERTAIN: reason]` — one fetch pass added unquoted claims of a "team of nine practitioners" and "a PayPal link for payments and WhatsApp for direct communication." Not corroborated by the verbatim-reproduction fetch; PayPal/chatbot chrome is discarded per extraction rules regardless. Excluded from confirmed body text.

### Enforcement
**Source:** https://adipven.com/enforcement-2/

Page heading: "Enforcement"

Body text (verbatim, confirmed consistent across two independent fetches): "Asia still faces with IP piracy problems. Asia is well connected via sea and air. Pirated goods can be easily transported within Asia and beyond." / "ADIPVEN™ assists clients in enforcing their IP rights. Asian countries which were former British colonies such as Malaysia, Singapore, India, Australia (Commonwealth countries) follow the English legal systems. Other countries like China, Indonesia, Taiwan etc. having their own unique legal systems. Therefore, it is important to identify the differences in the laws so that the clients' rights can be fully protected."

(Non-standard grammar "Asia still faces with..." and "...having their own unique legal systems" reproduced exactly as in source.)

No pricing, fee schedule, process-step list, or named individual contact appears in the fetched content for this page.

---

## Pricing & Commercial Terms

No prices, fee schedules, rate cards, or warranty terms were present in the fetched content of any of the 9 service pages or the Services overview page.

**Stated response-time commitment (source: About Us page, verbatim):** "ADIPVEN™ assures its clients that all their basic enquiries will be attended within 1 working day at no cost to you." / "All complicated enquiries will be attended to within 2 to 5 working days."

**Free initial consultation (source: Appointment page):** Page heading "Free Case Evaluation," body text: "Contacting the firm is free. We understand that the disputes facing you, your family or your business can seem daunting." However, the page's booking/contact form is broken — where a form would be expected, the page displays the literal error text: **"Error: Contact form not found."** This confirms the form is non-functional as of the fetch date, meaning the stated free-evaluation intake mechanism cannot currently be used via this page.

**Payment channel (source: Case Studies — "Adipven New Website Launched" announcement, verbatim):** "We've introduced a range of new content to the website, including an online payment facility powered by PayPal and it is directly accessible by clients." (Note: this announcement is undated on its source page; it describes a past website-relaunch event.)

No annuity/renewal fee amounts, litigation cost figures charged by the firm to clients, or SLA terms beyond the two response-time commitments above were found anywhere in the crawled content.

---

## Credentials, Certifications & Compliance

**Company registration:** "ADIPVEN (M) SDN. BHD. (968005-T / 201101039883)" (source: Contacts page — see also Contact & Identifying Information above).

**ISO 9001:2015 Quality Management System registration:** Confirmed by a dedicated firm announcement (source: Case Studies — "ISO 9001-2015 Registration Announcement"), verbatim: "I am pleased to announce that Adipven (M) Sdn. Bhd. has obtained ISO 9001-2015 Quality Management System Registration for the Provision of Intellectual Property Services including Patent, Trade Mark, Copyright, Industrial Design and Geographical Indications." The same announcement states: "We believe we are the first Intellectual Property firm in Malaysia to have obtained this recognition and we are in the midst of obtaining a confirmation from the Malaysia Book of Records" (the company states this as a claim; no independent Malaysia Book of Records confirmation is present in any fetched content). The announcement is signed by Ramakrishna Damodharan, Managing Director, and is undated on its source page.

This is corroborated by a separate source (Case Studies — "Women Scientists in Patenting Bring Double the Experience to the Table"), which states the firm is "a boutique Intellectual Property and Commercialisation (IP & C) firm based in Bangsar, Kuala Lumpur," described as "the only IP & C firm in Malaysia certified with ISO 9001:2015 standard and with an Eco Office status."

The Home page additionally displays two certification-related image files with no accompanying descriptive body text captured: one filenamed "ISO-9001_2015-UKAS_purple-01-1-1.jpg" (suggesting UKAS as the accrediting/certifying body) and one filenamed "Eco-Office-Logo-Trademark-01.png". `[UNCERTAIN: reason]` — the specific accrediting body (UKAS) and the "Eco-Office" status are suggested by image filenames and the one cross-reference above, but no page text gives a certificate number, issuing-body contact, or validity/expiry date for either credential.

**Individual professional registrations (agent/attorney credentials):** held by specific named staff, not the firm as a whole — see the People section below for each person's registration numbers (e.g., Registered Malaysian Patent Agent, Trademark Agent, Industrial Design Agent, Geographical Indications Agent, New Plant Variety and Grant of Breeder's Right Agent).

**Data protection compliance statement (source: multiple pages, e.g. Photos page):** the company states it is "committed to safeguarding all personal data as prescribed under the Malaysian Personal Data Protection Act 2010." This is boilerplate repeated across pages; recorded once here rather than per-page.

---

## Process / How It Works

None of the fetched service pages contained an explicit numbered or itemized "how it works" / engagement-process sequence. Each service page instead offers a single short descriptive passage stating what ADIPVEN™ "assists clients" with for that IP right (see Services / Products above). No step-by-step intake procedure, onboarding process, or timeline beyond the two response-time commitments recorded under Pricing & Commercial Terms was found in any fetched content.

---

## People

### Ramakrishna Damodharan — Managing Director
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/ramakrishna-damodharan/ ; also named (title "Managing Director") on the Home page and as signatory on several firm announcements in Clients & Case Studies.

Registrations: Registered Malaysian Patent Agent (Registration No. PA/2007/0177); Registered Malaysian Trademark Agent (Registration No. 4252); Registered Malaysian Industrial Design Agent (Registration No. ERP/2007/0016); Registered Malaysian Geographical Indications Agent (Registration No. 0006/GI); Registered New Plant Variety and Grant of Breeder's Right Agent (no registration number stated on either source).

Education: a degree in Applied Chemistry and a postgraduate degree in law from University Malaya (not further broken down by institution/date).

He handles patent, trademark, industrial design, geographical indications, new plant variety and grant of breeder's right, and copyright matters, and provides freedom-to-operate and infringement opinions. He provides litigation support to clients in Malaysia, Singapore, Korea, China, the United States, Europe, Russia, and Argentina (per the practitioners page).

The individual profile page states he is an accredited trainer by HRD Corp. Malaysia who delivers talks on IP and commercialization, and has been an invited speaker for UPM, USM, UTHM, UKM, and international agencies including UNESCO's ISTIC and the Hong Kong Trade Development Center (HKTDC). The practitioners page additionally states he was invited by UBD and BEDB.

The practitioners page states he is a founding board member of KGI Berhad (2015) and a committee member of the International Trademark Association (INTA); not stated on the individual profile page.

Languages (individual profile page only): fluent English, Malay and Tamil.

Personal: described as active in environmental NGOs / an environmental advocate, a sports enthusiast (football, badminton), and "a hardcore supporter of the English soccer team, Manchester United."

No contact details (email or phone) are stated on either profile page.

### Moganah Raman — Director of Accounts, Finance & HR
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/moganah-raman/ ; also named on the Home page.

Education: an honours degree in Accounting and Finance from the University of Greenwich, UK.

She started her career as an accounts and audit associate in a Kuala Lumpur audit firm, joined Adipven in 2014 as Accounts & Finance Executive, and was promoted to Director in July 2019. She is responsible for the firm's accounting/financial information and oversees department functions and employee management, and is described as well-versed in HR disciplines including compensation and benefits, training and development, employee relations, and recruitment and selection.

The individual profile page states she hails from Kuala Lumpur (not on the overview page).

Languages: fluent English, Bahasa Malaysia, Tamil and Mandarin.

Personal: described as cheerful and friendly; enjoys singing, listening to music, and spending time with family.

No contact details are stated on either page.

### Norlela Mat Lias — Director, Intellectual Property Services
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/norlela-mat-lias/

`[CONFLICTING: title]` — given as "Director, Intellectual Property Services" on the practitioners overview page vs. "Director, Intellectual Property Services (I)" on her individual profile page.

Registrations: Registered Malaysian Trademark Agent (Registration No. 4742); Registered Malaysian Industrial Design Agent (Registration No. ERP/2016/0013); Registered Malaysian Geographical Indications Agent (Registration No. 0034/GI); Registered New Plant Variety and Grant of Breeder's Right Agent (no registration number stated).

Education: degree in Business Administration from Universiti Utara Malaysia (UUM), Kedah.

Over six years of prior experience in construction and oil/gas industries, plus more than two years at another Kuala Lumpur IP firm before joining Adipven. Specializes in patent matters, especially filing and prosecution of international (PCT) applications, and industrial design matters. Manages portfolios for government agencies and universities; advises on patent prosecution, technical know-how, business commercialization strategy, and plant variety rights.

A separate source (Clients & Case Studies — "New Year Wishes from the Managing Director," referencing the 2016/2017 transition) states she was promoted to Senior Associate at that time and describes her as "a registered Trade Mark, Industrial Design, New Plant Variety and Grant of Breeder's Right Agent in Malaysia" — consistent with, though not identical in wording to, her registrations as listed above.

Languages: fluent English and Malay; basic conversational Mandarin.

Personal: enjoys reading, listening to music, and sightseeing.

No contact details are stated on either profile page.

### Mohd Faizul Mohd Yin — Director, Intellectual Property Services (II)
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/mohd-faizul-mohd-yin/ ; also named on the Home page and the Appointment page.

`[CONFLICTING: title]` — "Director, IP Services II" (practitioners page, individual page, and Home page) vs. "Director, Intellectual Property Services" without the "(II)" suffix on the Appointment page's "OUR PEOPLE" listing.

Registrations: Registered Malaysian Patent Agent (Registration No. MYA/2019/0040); Registered New Plant Variety and Grant of Breeder's Right Agent (no registration number stated).

Education: Diploma in Aerospace Engineering, Universiti Teknologi MARA, Malaysia; Master's Degree with Honours in Mechanical Engineering, University of Bath, United Kingdom.

Decades of experience in the IP field, including drafting patent specifications, prior-art and freedom-to-operate (FTO) searches, and technical analysis across engineering/technology sectors. Completed the South East Asian Patent Drafting (SEAD) course in 2008 through FICPI and the EPO. In 2016, selected by MyIPO and JPO for a specialized patent program in Tokyo. In April 2024, appointed Patentscope Super User by WIPO. The practitioners page additionally states he is an active member of the AOTS Alumni Society.

Languages: fluent English and Malay.

Personal: a stated deep interest in technology development and innovation strategy.

No contact details are stated on either profile page.

### Tharshini Maran — Financial Controller
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/tharshini-maran/

Education: Bachelor's Degree in Finance (Hons), Universiti Tenaga Nasional (UNITEN).

Born in Negeri Sembilan, raised in Malacca (individual page only). Previously served as secretary to Ramakrishna Damodharan before being promoted to Admin & Finance Manager. Manages the firm's docketing system (Adifids®), ISO and Eco Office compliance monitoring, and foreign-agent performance monitoring. Handles office supply procurement emphasizing Forest Stewardship Council (FSC) compliance for eco-friendly products. Manages cash reserves, fund transfers, accounts payable/receivable, invoice reconciliation, and payment processing to agents/suppliers.

Languages: fluent English, Bahasa Malaysia, Tamil and Mandarin.

Personal: enjoys dancing and watching movies.

No contact details are stated on either page.

### Nur Amalina Zamani — Senior Associate
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/nur-amalina-zamani/ ; also named on the Home page and the Appointment page.

`[CONFLICTING: credential detail]` — the practitioners overview page states her credential as "Registered Malaysian New Plant Variety and Grant of Breeder's Right Agent" only (no registration number). Her individual profile page states "Registered Malaysian Trademark and New Plant Variety and Grant of Breeder's Right Agent (Registration No. MYA/2024/0077)" — i.e. an additional Trademark Agent registration and a registration number not present on the overview page.

Education: Bachelor of Science in Biotechnology, Universiti Putra Malaysia.

Began her IP career in 2009; worked at multiple IP and law firms prior to Adipven, with expertise in local/international patent management, novelty searches, and patent specification drafting; has filed industrial design and trademark applications. Manages a portfolio of government-agency and university clients; advises on patent prosecution, technical know-how, business commercialization strategy, plant variety rights, and breeder's rights. Attended the MIPA Drafting Course and the WIPO Korea Summer School.

From Negeri Sembilan (individual page only).

Languages: fluent English and Malay.

Personal: enjoys outdoor activities; described as optimistic and goal-oriented.

No contact details are stated on either page.

### Dr. Soon Wei Chook — Associate
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/dr-soon-wei-chook/ ; also named on the Home page and the Appointment page.

Registration: Registered Malaysian New Plant Variety and Grant of Breeder's Right Agent (no registration number stated).

Education: Bachelor's degree and Ph.D. in Materials Science (specific institutions not stated on either page).

Four years as a postdoctoral researcher at Universiti Kebangsaan Malaysia and Universiti Malaya; research focus on nanomaterials for antimicrobial wound dressing, biomass utilization, catalysis, wastewater treatment, and spectroscopy. Peer-reviewer for scientific journals; has presented at international conferences.

`[UNCERTAIN: patent count/subject]` — individual profile page states he is "co-inventor of two patented methods in Malaysia involving silver nanomaterials and photocatalytic wastewater treatment"; the practitioners page states only, more generally, that he "co-invented patented items in Malaysia." Both pages state he was awarded the ITEX Silver Medal for "Graphene Oxide Cellulose Beads." The individual page additionally states research collaborations with industrial partners in electronics and latex manufacturing.

Languages: fluent English, Malay, Mandarin and Cantonese.

Personal: described as a curious learner interested in technology and machine learning; an animal lover.

No contact details are stated on either page.

### Mythili Thirunavukarasu — Associate
**Source(s):** https://adipven.com/practitioners/ ; https://adipven.com/lawyer/mythili-thirunavukarasu/ ; also named on the Home page and the Appointment page.

Registration: Registered Malaysian New Plant Variety and Grant of Breeder's Right Agent (no registration number stated).

Education: LL.B Honours degree, University of London (2018); "Top Student" award, Law of Tort, during LL.B studies (2017); Postgraduate Certificate in Laws (Medicine and the Law), University of London; currently pursuing an LL.M. Individual profile page additionally states a Professional Diploma in International Arbitration (not on the overview page).

Completed a law-firm internship in legal research, followed by pupillage at "one of the largest law firms in Malaysia," handling foreign IP portfolios and participating in "recce and raids conducted to combat the proliferation of counterfeit goods." Admitted as an Advocate & Solicitor of the High Court of Malaya following pupillage.

Languages: fluent English, Malay and Tamil; learning Mandarin.

Personal: interests include animals, music and dance (Indian classical dance / Bharatanatyam), watching movies, and reading fiction.

No contact details are stated on either page.

### Surain Satgunarajah — Senior Associate (title per Home page only — no biography available)
**Source(s):** named with title "Senior Associate" on the Home page only.

`[UNCERTAIN: reason]` — this person is listed by name and title on the Home page's personnel listing, but their dedicated profile page (https://adipven.com/lawyer/surain-satgunarajah/) returns an HTTP 404 (confirmed by re-fetching), and they do not appear anywhere on the Practitioners overview page (which lists eight people, all documented above). No biography, credentials, or further detail exists for this person in any crawled source. Whether they remain a current Adipven staff member cannot be confirmed from live site content.

### Other named individuals appearing outside the People pages (no dedicated profile — mentioned only in Case Studies/announcement content)

The following people are named in firm announcements or feature articles under Clients & Case Studies but have no page under `/lawyer/` or entry on the Practitioners page, so only what is stated in that specific article is recorded:

- **Wan Nurul Aisyah** — described (Case Studies: "Our Patent Attorney Aisyah Won the Best Paper Award," "Women Scientists in Patenting") as an Adipven Senior Associate/IP Associate and patent consultant; holds a Masters in Science (Industrial Science) from Universiti Tenaga Nasional (UNITEN) and a Degree in Biotechnology from INTI International University; fluent English and Bahasa Malaysia, basic Mandarin; won a "Session Best Paper" award presenting at an IICBE conference in Kota Kinabalu, Sabah; at time of the "Women Scientists" article had not yet sat the Malaysian Patent Agent examination.
- **Noorserra Aryecca Armat ("Serra")** — Senior Associate (Case Studies: "Women Scientists in Patenting"); Registered Malaysian Patent Agent; Biotechnology degree, Monash University, Australia; fluent English and Bahasa Malaysia, plus Bajau, Dusun and basic Mandarin; joined Adipven from another patent firm.
- **Dr Kumutha Priya** — Senior Associate (Case Studies: "Women Scientists in Patenting"); Ipoh-born; Ph.D. in Genetics and Molecular Biology, University of Malaya; Degree in Biomedical Science, University Tunku Abdul Rahman (UTAR); fluent English, Bahasa Malaysia, Tamil, basic Mandarin; previously a Graduate Research Assistant at the High Impact Research (HIR) Centre, University of Malaya; had recently passed the Malaysian Patent Agent examination at time of the article.
- **Chien Nee Yew** — Senior Associate (Case Studies: "Asia IP PPH Story"); interviewed alongside Adipven experts on the Patent Prosecution Highway (PPH) topic. No further biographical detail available (the article links to an external source not retrievable from the page).
- **Jayavaruman Subramaniam** — mentioned (Case Studies: "New Year Wishes from the Managing Director") as promoted to Senior Associate around the 2016/2017 transition; a Registered New Plant Variety and Grant of Breeder's Right Agent, stated to be becoming "a registered Patent, Trade Mark and Industrial Agent in Malaysia by middle of 2017."
- **Kazuki Ishigami** — mentioned (same source) as "the only active Japanese Patent Attorney based in Malaysia" on Adipven's team at that time, and a Registered Japanese Patent Attorney.

`[UNCERTAIN: reason]` — none of these six individuals appear on the current Practitioners page or have a current `/lawyer/` profile, so their current employment status at Adipven cannot be confirmed from live site content; they are recorded here only as historical/feature-article mentions.

---

## Clients & Case Studies

Sourced from the site's "Case Studies" (portfolio) content type — a distinct WordPress post type from the excluded News section. The following are case-law summaries and legal/regulatory updates (as opposed to firm self-announcements, which are grouped under News & Announcements below).

### Malaysia: YKL Engineering Defeated During Appeal
**Source:** https://adipven.com/case/malaysia-ykl-engineering-defeated-during-appeal/ · **Date:** Not shown

YKL Engineering Sdn. Bhd. sued Sungai Kahang Palm Oil Sdn. Bhd. and Profina Teknik Sdn. Bhd. for patent and copyright infringement regarding a "Fruit Bunch Splitter" machine (Patent No. MY-139512-A). The High Court ruled for YKL Engineering; the Court of Appeal reversed, finding for the defendants. The appellate court held the High Court failed to properly construe the patent itself (improperly delegating to expert witnesses) and that courts must apply "a purposive approach." It clarified that defendants may introduce additional prior-art examples at trial without prejudice if pleadings were adequate, rejected dismissal of expert reports merely for sharing similar phrasing ("similarities in phrases and words used...can be regarded as a norm or standard"), and applied the *Coco v A.N. Clark* test to hold that confidentiality alone does not exempt information from prior-art status. On copyright, the court held the plaintiff's drawings were substantially reproductions of prior art, defeating copyright protection and the infringement claim.

`[UNCERTAIN: this summary reflects an automated extraction pass over the source page rather than a direct verbatim HTML copy; substantive facts/holdings are as presented, but exact original sentence phrasing may differ slightly.]`

### Malaysia: Patent — Ultimate Decision on Dependent Claims' Survival in Court
**Source:** https://adipven.com/case/malaysia-patent-ultimate-decision-on-dependent-claims-survival-in-court/ · **Date:** Not shown

Federal Court decision on whether dependent patent claims automatically become invalid when their independent claim is invalidated. Parties: Merck Sharp & Dohme Group and Merck Sharp & Dohme (Malaysia) Sdn Bhd (Appellants) v. Hovid Berhad (Respondent). Patent: MY-118194-A for alendronate (Fosamax), one independent claim and 21 dependent claims. High Court dismissed the infringement action (30 Aug 2016), finding the independent claim obvious; Court of Appeal upheld (19 Sep 2017), ruling all dependent claims automatically invalid. Federal Court granted leave (26 Jun 2018) on the single question of whether dependent claims necessarily fail when the independent claim is invalidated. The majority judgment reversed precedent, holding dependent claims "may not necessarily automatically fail," and remitted the case to the High Court for individual claim-by-claim validity determinations.

`[UNCERTAIN: close paraphrase produced by the fetch tool rather than a raw HTML copy.]`

### Malaysia: How Patent Damages Are Assessed by Court
**Source:** https://adipven.com/case/malaysia-how-patent-damages-are-accessed-by-court/ · **Date:** Not shown

*Asia File Products Sdn Bhd v Brilliant Achievement Sdn Bhd, Lion File Marketing Sdn and Kho Kok Seang* (Court of Appeal), on compensatory-damages assessment for patent infringement. Patent: MY-137755-A, a tool-free box file with a clip mechanism. The Court held the plaintiff was entitled to loss-of-profit damages "arising from all the infringing products because it is probable that a reasonable customer of a box file would have purchased an infringing product thinking that such a product is a patented product." Reassessed damages: MYR1,558,472.45, with interest at 5% per annum from 30 March 2017 until full payment; no costs awarded for the prior assessment proceedings.

### Malaysia: Merck Sharp & Dohme Hits Another Obstacle
**Source:** https://adipven.com/case/malaysia-merck-sharp-dohme-hits-another-obstacle/ · **Date:** Not shown (Court of Appeal ruling described as issued January 2019)

Court of Appeal (Putrajaya), *Merck Sharp & Dohme Corp and Merck Sharp & Dohme (Malaysia) Sdn. Bhd. v Hovid Berhad*, re Malaysian Patent MY-118194-A (alendronate acid, "Fosamax," a dosing regime of 70 mg once weekly for a claimed seven-day period). High Court found Claim 1 invalid for lack of inventive step, invalidating all dependent claims. Court of Appeal unanimously upheld, citing *E I Du Pont De Nemours & Co v Imperial Chemical Industries Plc & Anor* (2007) for the principle that dependent claims survive only if independently redrafted as such. Matter stated as pending before the Federal Court for final appeal as of the source page.

`[UNCERTAIN: concerns the same patent (MY-118194-A) as the "Ultimate Decision on Dependent Claims" entry above; the two Adipven source pages appear to describe different stages of the same or a closely related Merck Sharp & Dohme v Hovid dispute — not reconciled here per extraction rules; each recorded as presented on its own page.]`

### Malaysia: Kingtime is Victorious
**Source:** https://adipven.com/case/malaysia-kingtime-is-victorious/ · **Date:** Not shown (ruling described as issued November 2018)

High Court of Malaya (Kuala Lumpur), *Kingtime International Limited and Gryphon Energy (Asia-Pacific) Sdn. Bhd v Petrofac E&C Sdn. Bhd*. Kingtime held patents MY-144898-A and MY-145004-A covering "Mobile Offshore Production Unit" (MOPU) technology; Gryphon Energy held a license. Dispute centered on interpreting "removably attached" in the patent claims (design-for-removal vs. attachment-method-only, with welding cited as prior art). The court applied the Essential Integers, Improver's, and Actavis' tests, all supporting infringement, and accepted the plaintiffs' expert interpretation that the wellhead deck and subsea conductor frame were modular building blocks. **Outcome:** the court found Petrofac infringed all three claims through construction, installation and operation of the Sepat MOPU (off Terengganu's coast).

### Malaysia: Patent Found to be Invalid
**Source:** https://adipven.com/case/malaysia-patent-found-to-invalid/ · **Date:** Not shown

High Court dispute, *Hong Yik Plastics (M) Sdn Bhd v Ho Shen Lee (M) Sdn Bhd and TNL Plastic Manufacturer Sdn Bhd*. Two issues: infringement, and patent validity. Under Section 59(3) of the Patents Act 1953 (5-year limitation period), the plaintiff failed to plead the infringement date; evidence showed infringement occurred before 10 Feb 2012, but suit was filed 13 March 2017 — the claim was dismissed as time-barred. On the defendants' invalidity counterclaim, the court found the inventor "relied heavily on his patent agent," who failed to disclose existing prior art in the application; the patent was invalidated for lack of novelty and incomplete disclosure. The counterclaim succeeded with costs.

`[UNCERTAIN: this entry and "Malaysia — Mirror, Mirror on the Wall" below both concern the same parties, Ho Shen Lee (M) Sdn Bhd and TNL Plastic Manufacturer Sdn Bhd, but describe different procedural aspects (patent invalidity vs. a judicial-conduct retrial appeal) — not reconciled here per extraction rules; each recorded as presented on its own source page.]`

### PPH MYIPO – CNIPA
**Source:** https://adipven.com/case/pph-myipo-cnipa/ · **Date:** Not shown; announcement text states effective 1 July 2018

Firm notice to clients/associates: effective 1 July 2018, the Intellectual Property Corporation of Malaysia (MyIPO) started a pilot Patent Prosecution Highway (PPH) program with the Chinese National Intellectual Property Administration (CNIPA), for a three-year period (until 30 June 2020). The program enables sharing of search/examination results between MyIPO and CNIPA to accelerate examination of corresponding applications. Clients are encouraged to use the initiative to expedite Malaysian applications where the corresponding Chinese application has a positive search/examination report or grant. The notice states MyIPO already had PPH programs with the Japanese Patent Office and the European Patent Office, with further expansion expected.

### Cambodia: European Patents Can Now Be Validated in Cambodia
**Source:** https://adipven.com/case/cambodia-european-patents-can-now-be-validated-in-cambodia/ · **Date:** Not shown; effective date stated as 1 March 2018

The EPO President and the Cambodian Minister of Industry and Handcraft signed a validation agreement effective 1 March 2018, making Cambodia the first country in Asia to validate European patents, as part of the EPO's 38-member-state validation framework. Requirements to validate a European patent in Cambodia: (1) EU filing date on/after 1 March 2018; (2) alignment with Cambodian patent law (e.g., pharmaceutical products excluded from protection until TRIPS obligations expire); (3) claims translated into Khmer. Validation fee: EUR180, payable to the EPO within 6 months of publication of the European Search Report (2-month grace period available with a 50% surcharge); a request to validate as a Cambodian national patent must then be filed with the Ministry of Industry and Handicraft within 3 months of EPO grant.

### India: Requirements of Working Statements
**Source:** https://adipven.com/case/india-requirements-of-working-statements/ · **Date:** Not shown

Discusses a Delhi High Court order on submission of "working statements" (Form 27) for Indian patents, due annually by 31 March for the preceding calendar year; failure to file complete/correct information can result in fines and criminal proceedings, including imprisonment up to 6 months. The Court held that details of licenses/sub-licenses cannot be withheld as "confidential" and directed the Indian Patent Office to act against non-compliant patentees; it also rejected the argument that Form 27's vagueness excuses non-compliance. The order was not final (appeal to the Supreme Court of India possible) but working-statement filing remains mandatory in the interim.

### Malaysia: Court of Appeal Held Skyworld Mark is Well-Known
**Source:** https://adipven.com/case/malaysia-court-of-appeal-held-skyworld-mark-is-well-known/ · **Date:** Not shown

*Skyworld Development Sdn Bhd & Anor v Skyworld Holdings Sdn Bhd & Ors* — trademark infringement, passing off, and unlawful interference with trade. Plaintiffs (real estate/property development) held registered ownership of "SkyWorld" since 2014; defendants (tourism businesses in Sabah) used "Skyworld"/"Sky World"/"Sky World City Sabah." High Court dismissed the claim (marks visually different, similarities coincidental, insufficient goodwill shown); Court of Appeal unanimously reversed. Key holdings include: infringement under s.38 Trade Marks Act 1976 requires ownership of a valid registered mark, unauthorized use, and resulting deception/confusion (citing *Low Chi Yong v Low Chi Hong* [2018] 1 MLJ 175); company/business/domain-name registration does not itself confer trademark rights nor preclude an infringement action (citing *Celine SARL v Celine SA* (2007) C-17/06 for the "use in relation to goods or services" two-stage test); computer-generated emails are admissible without calling the maker as witness under s.90A Evidence Act 1950; passing off does not require the plaintiff's goodwill to be "well-known," only "distinctive to Plaintiffs" (applying *Reckitt & Colman Products Ltd v Borden Inc.* [1990] 1 WLR 491), though the CoA agreed no damage was proven; and that a finding of trademark infringement/passing off automatically makes out the tort of unlawful interference with trade.

### Malaysia: A Decision on Relevance and Cause of Action Relating to Property Managers
**Source:** https://adipven.com/case/malaysia-a-decision-on-relevance-and-cause-of-action-relating-to-property-managers/ · **Date:** Not shown

Appraisal Property Management Sdn Bhd, JLL Property Services (Malaysia) Sdn Bhd, and Jones Lang Wootton Ltd (Appellants) v Singham Sulaiman Sdn Bhd (Respondent) — Court of Appeal, consolidated suits on passing off and trademark removal. High Court had ruled for the respondent on both suits; Court of Appeal allowed the appeal, ordering retrial, holding the High Court had wrongly focused on an unpleaded illegality issue (alleged breach of Section 23, Valuers, Appraisers and Estate Agents Act 1981) rather than the pleaded passing-off/trademark issues (citing *Asia Television Ltd & Anor v Viwa Video Sdn Bhd* [1984] 2 MLJ 304 on the need for a nexus between alleged illegality and the cause of action). The Court of Appeal also held the High Court had misapplied Section 165 of the Evidence Act 1950 in compelling document production on the illegality point, and that the corporate veil was improperly pierced for a non-pleaded purpose.

`[Note: this and "Malaysia: JLLP Appeal's Allowed" below both concern the same underlying JLLP v Singham Sulaiman litigation, described on two separate Adipven source pages — recorded independently per extraction rules; minor party-name framing differs between the two pages' own wording.]`

### Malaysia: Trademark Infringement and Obligation of Online Platform Providers Defined by Court
**Source:** https://adipven.com/case/malaysia-trademark-infringement-and-obligation-of-online-platform-providers-defined-by-court/ · **Date:** Not shown

*A & M Beauty Wellness Sdn. Bhd. v Shopee Mobile Malaysia Sdn. Bhd.* — IP Court, Kuala Lumpur. Plaintiff sought a mandatory interim injunction compelling Shopee to remove listings allegedly infringing its registered "AM PROFESSIONAL SKIN CARE" mark. Application dismissed: plaintiff failed to prove a serious question to be tried (Shopee provided a takedown mechanism the plaintiff did not use; the mark was registered to a third party, Chua Siok, and the plaintiff's unregistered assignment gave it no locus standi); balance of convenience and status quo favoured the defendant; the plaintiff's undertaking as to damages was inadequate. The Court held mandatory interim injunctions additionally require an unusually strong, clear case with special circumstances, not met here — relieving online platform providers of an obligation to actively police every listing for infringement. The source page notes "it remains to be seen if the decision will withstand the test of time."

### Malaysia: Traders Can Be Found Liable for the Tort of Passing-Off
**Source:** https://adipven.com/case/malaysia-traders-can-be-found-liable-for-the-tort-of-passing-off/ · **Date:** Court of Appeal judgment dated 12 February 2019

*Lifomax Woodbuild Sdn Bhd v Amsteel Mills Sdn Bhd*. High Court (24 Sep 2013) found the appellant liable for passing off after supplying deformed steel bars represented (via fake Mill Test Certificates/Product Tags) as the respondent's to Mammoth Empire Construction Sdn. Bhd. On appeal, the appellant argued it was merely a reseller (goods purchased from NBH Marketing Sdn. Bhd.), not a manufacturer. The Court of Appeal held a trader can be liable for passing off regardless of manufacture — once resold to Mammoth, the goods became "the Appellant's goods" for tort purposes — and dismissed the appeal with costs.

### Malaysia: Understanding the Value of Trademark Co-Existence in Other Jurisdictions
**Source:** https://adipven.com/case/malaysia-understanding-the-value-of-trademarks-co-existence-in-other-jurisdictions/ · **Date:** Registrar's decision dated 3 May 2018; High Court appeal filed 2 July 2018

High Court, *Merck KGAA v Xtalic Corporation*, appeal against the Registrar of Trade Marks' dismissal of Merck's opposition to Xtalic's "XTALIC" mark (Class 2) application (filed 20 July 2009) as against Merck's registered "XIRALLIC" mark (Classes 1, 2, 37, 42; first use Malaysia August 2002 / internationally 2000; registered in numerous countries). The High Court dismissed all five grounds of appeal, finding no likelihood of confusion given differing goods purpose/trade channels (Merck: aesthetic coatings; Xtalic: engineering-functionality coatings), and treated co-existence of the marks in other jurisdictions (including a similar dismissal by the Korean IP Office) as "an indication that there is no likelihood of deception or confusion." Appeal disallowed, Registrar's decision upheld, costs awarded against Merck.

### Malaysia: Effect of Disclaimers on the Scope of a Trademark
**Source:** https://adipven.com/case/malaysia-effect-of-disclaimers-in-the-scope-of-trademark/ · **Date:** Court of Appeal judgment dated 17 July 2019; case reported at [2020] 1 MLJ 101

*Nor Yanni bt Adom & Anor v Ortus Expert White*. Respondent owned registered mark "Royal Expert White" (with crown device, disclaiming exclusive rights to "Royal" and "Expert White"). Appellants (a dealer and a distributor) sold a competing "Real Expert White" product. High Court found the appellants liable for dealership-agreement breach, trademark infringement, and passing off. Court of Appeal reversed: since "Expert White" was disclaimed and therefore unprotected, the only striking similarity between the marks was the disclaimed wording, so the marks were not confusingly similar and there was no infringement. On passing off, the Court of Appeal gave weight to a Ministry of Health press statement that banned "Royal Expert Whitening Cream" for containing mercury, finding this — not the appellants' conduct — destroyed the respondent's claimed goodwill. Appeal unanimously allowed with costs; High Court decision set aside.

### Malaysia: Biscuits Battle in Court
**Source:** https://adipven.com/case/malaysia-biscuits-battle-in-court/ · **Date:** Not shown (Court of Appeal stage discussed; High Court decision precedes it)

*Munchy Food Industries Sdn Bhd v Huasin Food Industries Sdn Bhd* (High Court), concerning the "LEXUS" biscuit mark (registered 23 Jan 1998) vs. the defendant's "LEX" mark application (25 Sep 2015). High Court: dismissed the defendant's counterclaim to expunge the plaintiff's mark (plaintiff was the first bona fide user in Malaysia, so the s.14(1)(a) TMA confusion bar does not apply to a 1st user); held the defendant could rely on a third party's mark (Toyota's LEXUS) as an expungement ground in principle but failed to prove confusion with it; ruled Wikipedia/internet search evidence inadmissible for lack of authorship/source information; found house-brand/sub-brand combinations can each be independently distinctive under s.37(c) TMA; and found passing off established given get-up similarities. Plaintiff's claim allowed with costs; defendant's counterclaim dismissed. On the defendant's (Huasin's) further appeal to the Court of Appeal, that court held both parties were genuine traders, that the Trade Marks Act is not meant to grant monopolies, and that courts should consider whether parties ought to have sought mark co-existence orders rather than pursue narrow technical arguments from jurisdictions without a co-existence doctrine.

`[UNCERTAIN: the source page does not state the Court of Appeal's ultimate disposition (allowed/dismissed) of Huasin's appeal — only the two holdings quoted are given.]`

### Malaysia: JLLP Appeal's Allowed
**Source:** https://adipven.com/case/malaysia-jllp-appeals-allowed/ · **Date:** Court of Appeal judgment described as issued March 2019

Companion Court of Appeal decision to the "Relevance and Cause of Action" entry above, in the same *JLLP v Singham Sulaiman Sdn Bhd (SSSB)* litigation (party names here given as "JLLP" collectively — Appraisal Property Management Sdn. Bhd., JLL Property Services (Malaysia) Sdn. Bhd., and Jones Lang Wootton Ltd — vs. "SSSB"). Covers two suits: (1) passing off of real estate services under "Jones Lang LaSalle"/"JLL," with a counterclaim that SSSB itself passed off services as JLL-Group-affiliated; and (2) JLLP's application to remove SSSB's registered "Jones Lang Wootton" composite mark, alleging it was registered in breach of a 1993 Deed of Sub-Licence and 1992 Deed of Covenant. Background traces a chain of assignments culminating in JLWL holding the historical IP rights, a 2002 "Global Operating Framework" (GOF) between the parties, SSSB's 2006 trademark registration (allowed by the Registrar), and GOF's termination in 2012. High Court ruled for SSSB on both suits. Court of Appeal held defendants' counsel had diverted the High Court onto collateral issues (illegality, corporate-veil, loan documents), causing it to lose focus on the core passing-off/expungement issues, allowed the appeal with costs, set aside the High Court's decision, and ordered a retrial before a different judge.

### Malaysia: Passing Off Much?
**Source:** https://adipven.com/case/malaysia-passing-off-much/ · **Date:** Not shown

Guangzhou Light Industry & Trade Group Ltd, Guangzhou Eaglecoin Enterprises Group Corporation (a/k/a Guangdong Cannery), and Kim Guan Hap Kee Sdn Bhd (Plaintiffs) v Lintas Superstore Sdn Bhd (Defendant), concerning canned "Eagle Coin" fried dace sold in the defendant's Kota Kinabalu supermarket. The third plaintiff, sole registered user of the mark in Malaysia, established goodwill and showed the defendant's product (though of common origin) did not meet Malaysian "halal" requirements the plaintiff's product met, risking reputational damage from consumer confusion. All non-arguable facts favoured the plaintiffs (registered ownership, authorized marketer, sole registered user, defendant neither owner nor registered user, no consent given). **Outcome:** plaintiffs succeeded on both trademark infringement and passing off; defendant ordered to pay costs of MYR30,000.00.

### Malaysia: Estoppel and Breach of Contract
**Source:** https://adipven.com/case/malaysia-estoppel-and-breach-of-contract/ · **Date:** High Court decision dated 7 August 2018; Court of Appeal case reported at [2019] 9 MLJ 315

*Mohamad bin S Ahmad & Ors v Lembaga Pengelola Dewan Bahasa dan Pustaka*. Partners of Darul Fikir (exclusive distributors/copyright owners of "Mushaf Al-Quran Bertajwid dan Berwarna") sought to enjoin the respondent from issuing an open tender to a third party to publish the book without their written consent, alleging breach of a 2 September 2016 contract. High Court found no breach (the one-year contract had lapsed, no supplemental contract signed, respondent had paid in full). Court of Appeal held the High Court erred in finding no copyright was conferred on the appellants under Clauses 13.1/14.1 of the contract, and held that contractual statements of fact (Clauses 13.1, 15.1) bind the parties by estoppel even after contract expiry — making it inequitable for the respondent to permit third-party publication without the appellants' consent. Appeal allowed with costs; High Court decision set aside.

### Malaysia: Who Owns the Bike?
**Source:** https://adipven.com/case/malaysia-who-owns-the-bike/ · **Date:** Decision discussed dated 30 October 2019

Honda Giken Kogyo Kabushiki Kaisha ("Honda," Plaintiff/Appellant across suits) v. DNC Asiatic Holdings/Demak Marketing/Demak Motor Corporation (Suit 36, re the "Demak" motorcycle) and MForce Bike Holdings/Malaysian Formula Bikes (Suit 37, re the "SYM E-SMART" motorcycle), on copyright in Honda's EX-5/EX-5 Dream motorcycle design (created Japan 1985, launched Malaysia 1987). High Court allowed Honda's claim in Suit 36, dismissing the defendants' counterclaim, but (per the source text) dismissed Honda's damages claim `[UNCERTAIN: source text does not clearly specify to which suit/defendant this damages dismissal applies]`. On appeal (Appeal 2, concerning Suit 37, decided first by party agreement to determine the course of the other two appeals), the Court of Appeal held copyright subsisted in the EX-5 works under the Berne Convention's national-treatment principle (Malaysia obligated to protect Japanese-origin works equally) and that Honda had adduced sufficient ownership evidence. Appeal 2 unanimously dismissed with costs of RM20,000.00 against the appellants; High Court decision reaffirmed.

### Malaysia — Mirror, Mirror on the Wall, Who's the Fairest of 'Em All?
**Source:** https://adipven.com/case/malaysia-mirror-mirror-on-the-wall-whos-the-fairest-of-em-all/ · **Date:** Not shown

*Ho Shen Lee (M) Sdn Bhd v TNL Plastic Manufacturer Sdn Bhd* — a judicial-conduct appeal. The trial judge repeatedly interrupted/interjected during the plaintiff's witness examinations; the plaintiff's claim was dismissed and the defendant's counterclaim allowed. The plaintiff appealed for a retrial on grounds of unfair judicial treatment (rather than improper evidence admission). The Court of Appeal found the trial judge "not only seriously transgressed the fundamental principle that she should have remained neutral, but she also acted in a manner which was, at times, manifestly unfair and hostile to the plaintiff" — sufficient by itself to warrant reversal. **Outcome:** new trial ordered before another judge; High Court order set aside; no costs charged for the appeal.

`[Note: this entry and "Malaysia: Patent Found to be Invalid" above both involve Ho Shen Lee (M) Sdn Bhd and TNL Plastic Manufacturer Sdn Bhd as parties but describe different aspects of the litigation — not reconciled here per extraction rules.]`

### Malaysia: Man Accused of Malicious Cyber-Attack Against Own Company Released and Acquitted
**Source:** https://adipven.com/case/malaysia-man-accused-of-malicious-cyber-attack-against-own-company-released-and-acquitted/ · **Date:** Attack occurred 27 September 2012

Loh Guo Shi was acquitted by the Magistrate's Court after the prosecution "failed to prove its prima facie case." Data was deleted from a server belonging to Sistem Exabyte Network Sdn. Bhd. around 12:30am on 27 September 2012; the attacker's IP address was traced to the defendant's computer, but forensic analysis (conducted 27 Nov 2012, after the laptop was surrendered 28 Sep 2012 and used twice in the interim) found no evidence the laptop was used during the 12:30–1:30am attack window, so the prosecution could not establish the necessary connection.

### Malaysia: Jurisdiction of Court is Defined
**Source:** https://adipven.com/case/malaysia-jurisdiction-of-court-is-defined/ · **Date:** Not shown

A copyright infringement case `[UNCERTAIN: specific plaintiff/defendant names not given on the source page]` before the Penang High Court, concerning a defendants' application to transfer proceedings to the Kuala Lumpur High Court under Section 25(2)/Paragraph 12 of the Schedule to the Courts of Judicature Act 1964, Order 92 rule 4 of the Rules of Court 2012, and/or inherent jurisdiction. The High Court found the statutory application defective (the cited provision grants powers but not transfer jurisdiction) and declined to invoke inherent jurisdiction, dismissing the application. **Outcome:** the Court of Appeal overturned this, allowing the transfer of the case to the Intellectual Property Division of the Kuala Lumpur High Court.

### Copyright Article — Telekung (Malaysia)
**Source:** https://adipven.com/case/copyright-article-telekung/ · **Date:** Not shown

*Siti Khadijah Apparel Sdn Bhd v Ariani Textiles & Manufacturing (M) Sdn Bhd* (High Court of Malaya), on whether copyright subsists in "telekung" (a garment worn by Muslim women during prayer). The Court held: (1) the telekung's design drawings constitute a "graphic work" and the garment itself an "artistic work" under s.3 Copyright Act 1987, though not shown to be a "work of artistic craftsmanship"; (2) functionality does not bar copyright under s.7(2A) (the telekung also provides comfort/elegance, not pure function), and the plaintiff satisfied all ownership conditions (original character, material form, made by a qualified-person employee, first published in Malaysia, not separately registered as an industrial design); (3) copyright had not ceased under former s.7(6) (repealed by Act A1402/2012) since a telekung is not an "industrial design" reproduced by an "industrial process"; (4) the defendant infringed by reproducing/distributing a substantially similar telekung (applying *Designers Guild* and the "Laddie's Test" for altered copying), and lack of knowledge of the plaintiff's copyright is not a defence to infringement (citing *Elster Metering Ltd & Anor v Damini Corporation Sdn Bhd & Anor* [2012] 1 LNS 959), though it may bear on damages quantum.

### Malaysia: Famous Filmmaker & Co. Continue the Fight
**Source:** https://adipven.com/case/malaysia-famous-filmmaker-co-continue-the-fight/ · **Date:** Not shown; Federal Court leave stage pending "at the time of writing" per the source page

Elias Idris (author of the novel "Aku Bohsia") v. filmmaker Datuk Mohd. Yusof Md Aslam, his son Mohd Syamsul Md Yusof, and Skop Productions Sdn.Bhd., alleging the movie "Bohsia: Jangan Pilih Jalan Hitam" infringed his novel's copyright (similar plot, characters, themes involving sexually victimized girls, illegal racers, and paternal abuse). High Court dismissed; Court of Appeal reversed, finding substantial, non-coincidental similarity and holding that indirect causal connection (via prior publication/public availability of the novel) suffices to establish access, and should not be given a restrictive interpretation. Court of Appeal found infringement for the appellant/plaintiff. Respondents then obtained Federal Court leave to appeal on: (1) whether publication alone satisfies the "causal connection" requirement; and (2) whether courts have a legal duty to examine/evaluate both works under the *Megnaway Enterprise Sdn Bhd v Soon Lian Hock* [2009] 3 MLJ 525 test. No Federal Court hearing date had been fixed as of the source page.

### Malaysia: A Copyright Saga
**Source:** https://adipven.com/case/malaysia-a-copyright-saga/ · **Date:** Not shown

Chuah Aik King (sole proprietor of "B Three Technology") v Keydonesoft Sdn. Bhd. (High Court of Malaya, Kuala Lumpur), re copyright in the "B3 Café Internet Café Billing Management with MyCard Solution Software" and "Coin River Net Café Management System" programs, allegedly infringed by the defendant's "Keybilling Management System." The plaintiff claimed authorship via commissioning China-based ZYS (per a 13 January 2009 Copyright Agreement) and sought damages of RM1,100,000 / approximately "USD27,6073.00" `[UNCERTAIN: this USD figure appears malformed/typo'd in the source and is reproduced exactly as extracted]`. The defendant had separately and directly commissioned ZYS for its own customized software, with copyright vesting in ZYS. The Court held functions of a computer program are not copyrightable ideas under s.7(2A), and that the plaintiff failed to discharge his burden of proving authorship/ownership — notably by not calling the stated author (Mr. Feng Jiang of ZYS) as a witness, triggering an adverse inference, and by being found not a credible witness. Only a copyright owner may sue under s.37(1). **Outcome:** suit dismissed with costs for lack of standing/proof of ownership.

---

## News & Announcements

Firm self-announcements published under the site's "Case Studies" (portfolio) content type — distinct from, and not part of, the excluded News blog-post section. All are signed by Ramakrishna Damodharan, Managing Director, Adipven (M) Sdn. Bhd., unless noted.

### SST Announcement
**Source:** https://adipven.com/case/sst-announcements/ · **Date:** Not shown; content references an effective date of 1 September 2018

States that, per the Malaysian Government's announcement on Sales and Services Tax (SST), SST became applicable to all taxable services rendered from 1 September 2018. Enquiries directed to info@adipven.com.

### ISO 9001-2015 Registration Announcement
**Source:** https://adipven.com/case/iso-9001-2015-registration-announcement/ · **Date:** Not shown

Announces that Adipven (M) Sdn. Bhd. obtained ISO 9001-2015 Quality Management System Registration "for the Provision of Intellectual Property Services including Patent, Trade Mark, Copyright, Industrial Design and Geographical Indications," stating the company believes it is the first IP firm in Malaysia to obtain this recognition (confirmation from the Malaysia Book of Records stated as pending at time of writing). States the certification process took "almost a year" of process documentation and internal audits. (See Credentials, Certifications & Compliance above for cross-referenced corroboration.)

### Adipven New Website Launched
**Source:** https://adipven.com/case/adipven-new-website-launched/ · **Date:** Not shown

Announces the launch of a new website featuring a "clean design," responsive layout, a PayPal-powered online payment facility, and a QR code linking to an "ADIPVEN" mobile app (iOS and Android) providing IP/commercialization updates. States plans to introduce AI features "by end of this year" (year not specified) for real-time client advice.

### Adipven is Expanding
**Source:** https://adipven.com/case/adipven-is-expanding/ · **Date:** References an effective address-change date of 3 April 2017; states the firm "was founded on 2 January 2012"

States Adipven was founded 2 January 2012 and, as of 3 April 2017, expanded its office space (additional suite A-33-3A at the Menara UOA Bangsar address — see Contact & Identifying Information above for the resulting address conflict with the current Contacts page). Phone, fax, and email stated as unchanged.

### New Year Wishes from the Managing Director
**Source:** https://adipven.com/case/new-year-wishes-from-the-managing-director/ · **Date:** Not shown; content references the 2016–2017 year transition

Thanks clients/associates for the year; announces promotions of Norlela Mat Lias and Jayavaruman Subramaniam to Senior Associate, and describes Kazuki Ishigami as "the only active Japanese Patent Attorney based in Malaysia" then on staff. Mentions plans to "launch our online television" to showcase client products/services.

---

## People — Staff feature articles (see also People section above)

The following Case Studies entries are staff human-interest pieces rather than case-law or firm announcements; the individuals they describe (Wan Nurul Aisyah, Noorserra Aryecca Armat, Dr Kumutha Priya, Chien Nee Yew) are catalogued in the People section above under "Other named individuals," since none has a current dedicated profile page.

### Our Patent Attorney Aisyah Won the Best Paper Award
**Source:** https://adipven.com/case/our-patent-attorney-aisyah-won-the-best-paper-award/ · **Date:** Not shown

First-person account (presumed author: Wan Nurul Aisyah, though the source page as extracted does not itself name the author) describing a transition from science research into IP work at Adipven, and winning a "Session Best Paper" award presenting "Phycocyanin fluorescence in whole cyanobacterial cells as bioindicators for the screening of Cu2+ and Pb2+" at an International Institute of Chemical, Biological and Environmental Engineering (IICBE) conference in Kota Kinabalu, Sabah, before an international academic audience.

### Asia IP PPH Story
**Source:** https://adipven.com/case/asia-ip-pph-story/ · **Date:** Not shown

Short announcement that Senior Associate Chien Nee Yew was interviewed, together with Adipven's Asia-based experts, on the Patent Prosecution Highway (PPH) topic, linking to an external article. `[TRUNCATED IN SOURCE: the linked external article's content was not retrievable from this page.]`

### Women Scientists in Patenting Bring Double the Experience to the Table
**Source:** https://adipven.com/case/women-scientists-in-patenting-bring-double-the-experience-to-the-table/ · **Date:** Not shown

Feature article profiling three Adipven Senior Associates — Noorserra Aryecca Armat ("Serra"), Wan Nurul Aisyah, and Dr Kumutha Priya — on women's contributions in patenting, including individually attributed first-person quotes on their career paths into IP work, and closing with the statement (quoted in Credentials, Certifications & Compliance above) that Adipven is "the only IP & C firm in Malaysia certified with ISO 9001:2015 standard and with an Eco Office status," describing the firm as "a boutique Intellectual Property and Commercialisation (IP & C) firm based in Bangsar, Kuala Lumpur."

---

## Testimonials

The Home page displays three client testimonials with attribution. These are presented by the company as genuine client quotes; authenticity cannot be independently verified from the fetched content, so each is framed as a company-stated claim:

- The company states a client said: "ADIPVEN™ provides the best service at the very affordable price and promptly." — attributed to C. Ramamurthy, India.
- The company states a client said: "We use Adipven for all our IP matters throughout the world and Adipven gives excellent service and had never disappointed us" — attributed to Sally Chen, Malaysia.
- The company states a client said: "We choose ADIPVEN™ as they have high level of understanding and appreciation of our products and brands" — attributed to Williams C. Hans, United States of America.

---

## Company Background

**Tagline (Home page):** "The Best IP Protection & IP Strategies"

**Tagline (About Us page):** "ADIPVEN™ – Your Asian Intellectual Property Partner"

**Founding date:** stated in a firm announcement (Case Studies — "Adipven is Expanding") as "founded on 2 January 2012." No founding narrative on the About Us page itself gives a specific date. `[CONFLICTING/UNCERTAIN note: the "New Year Wishes" announcement, referencing the 2016/2017 transition, states the firm "has expanded greatly since our entrance into the business five years ago," consistent with a circa-2012 founding.]`

**Company identity (About Us, verbatim):** "Welcome to ADIPVEN™, one of Asia's most established and leading intellectual property (IP) consultancy and commercialization firm." "ADIPVEN™ is headquartered in Kuala Lumpur (KL), Malaysia." The company states: "With our recognized leadership in applying legal service and technology innovation, we deliver commercial advantage to clients."

**Founding narrative (About Us, verbatim):** "ADIPVEN™ attorneys have extensive experience in IP and commercialization of IP." "ADIPVEN™ is founded by a group of IP and commercialization experts who see the importance of setting up an Asian-wide firm with international and local experts." "ADIPVEN™ is proud to be part of the Asian revolution and will continue to work to ensure that Asia continues to be hub for IP and commercialization."

**Stated client philosophy (About Us, verbatim):** "Staying true to its tagline, ADIPVEN™ – Your Asian Intellectual Property Partner, ADIPVEN™ treats its clients as its own business partners and therefore the assistance that ADIPVEN™ provides to its clients is more than what clients demand as ADIPVEN™ wants its clients succeed in all their undertakings." Stated mantra: "ADIPVEN™ will only be successful if our clients are successful." "Clients are our partners."

**Stated differentiator (About Us, verbatim):** "Unlike other IP practitioners who may be able to advise you purely on IP aspect, ADIPVEN™ is able to advise you on both IP and commercialization as ADIPVEN™ has experts in both fields." "ADIPVEN™ will understand clients' needs; will help clients to leverage their goodwill and brand through the best strategies."

**Services listed (About Us page, verbatim list):**
- "Advising the best IP protection and IP strategies"
- "Conducting various types of searches, such as novelty patent search, patent landscape search, patent infringement search, availability trademark search, trademark infringement search, novelty industrial design search and industrial design infringement search"
- "Filing patent, trademark, industrial design and copyright applications"
- "Patent, trademark and industrial design monitoring service"
- "Trademark oppositions"
- "IP renewals and annuities"
- "New Plant Variety Rights"
- "Geographical Indication (GI)"
- "IP valuation"
- "IP audit"
- "Commercialization strategies"
- "Trainings and talks on IP and commercialization"
- "Licensing, assignment, merger and acquisition"
- "Enforcements"
- "Litigation support for patent, trademark, industrial design, copyright, trade secret, confidential information, geographical indication infringement and revocation cases. This is done together with our associate law firm."

**Team composition (About Us, verbatim):** "ADIPVEN™ IP experts comprise a talented team of lawyers, Malaysian patent attorneys, Malaysian trademark attorneys, Malaysian industrial design attorneys, Malaysian copyright attorneys, Malaysian geographical indications attorneys, Malaysian new Plant variety and plant breeder's rights attorneys as well as commercialization experts." "Our patent attorneys come with various technical backgrounds such as chemistry, biotechnology, electrical engineering, mechanical engineering, information and communication technology (ICT)." "All its experts are experienced practitioners and have worked in the area of intellectual property and commercialization for many years."

**Geographic scope (About Us, verbatim):** "ADIPVEN™ assists its clients in filing applications for patents, trademarks, industrial designs in the entire Asian region directly in the countries where ADIPVEN™ has its own offices and through strategic exclusive arrangements ADIPVEN™ has with its associates and agents in the countries where ADIPVEN™ does not have its own offices." "From its headquarters in KL, ADIPVEN™ acts as a one-stop IP and commercialization centre to coordinate all our clients IP and commercialization matters in Asia, particularly in Malaysia, India, Singapore, Vietnam, Indonesia, Thailand, The Philippines etc." "ADIPVEN™ also works with the best IP and commercialization firms around the world in ensuring our clients rights are fully secured and properly managed not only in Asia but also in the Americas and Europe."

**Named personnel listed on the Home page (names and titles as shown there):** Ramakrishna Damodharan (Managing Director), Moganah Raman (Director of Accounts, Finance & HR), Norlela Mat Lias (Director, IP Services I), Mohd Faizul Mohd Yin (Director, IP Services II), Surain Satgunarajah (Senior Associate), Nur Amalina Zamani (Senior Associate), Dr. Soon Wei Chook (Associate), Mythili Thirunavukarasu (Associate), Tharshini Maran (Financial Controller). Full biographical detail for each is in the People section above.

**Photo gallery (Photos page):** four gallery entries, titles only, no captions or dates beyond what the titles themselves imply: "ADIPVEN (M) SDN BHD," "BADMINTON SESSION TIME!," "ADIPVEN TRIP 2017," "NEW OFFICE GRAND OPENING." These function as informal signals of company history/events (a 2017 company trip, a new office opening, an internal social/badminton event) but no further descriptive text was found.

**Appointment page — additional content flagged as likely non-authentic template material:** the Appointment page (see Pricing & Commercial Terms above for its broken contact form) also displays "WHO WE ARE," "LEGAL AWARDS," and a "FEATURED NEWS & INSIGHTS" item referencing "Singapore: Court of Appeal Reverses High Court's Decision" (dated 24 April 2013), plus generic phrasing about "some of the world's most active M&A, real estate, financial services, litigation and corporate risk practices." `[UNCERTAIN: reason]` — this content reads as generic law-firm website template/demo material rather than content specific to ADIPVEN's actual IP-focused practice, is not corroborated by any other fetched page, and its accuracy as a description of ADIPVEN is questionable. Recorded here only because it is literally present on the live page.

---
## Extraction Notes

### Gaps and uncertainties

- **Services pages:** No page among the 10 fetched (9 service pages + overview) contained pricing, fee schedules, warranty terms, SLAs beyond the two general response-time commitments recorded under Pricing & Commercial Terms, or a named individual contact for a specific service line. The "Find Out More" link present on each service page did not resolve to a distinguishable destination in fetched content.
- **Services overview page** (`/services/`) inconsistently returned a practitioner-name list and service-category bullet list across repeated fetches — flagged `[CONFLICTING]` and excluded from confirmed body content.
- **Geographical Indications page:** second/third body sentences were paraphrased differently across two fetch attempts; exact character-for-character wording not fully confirmed.
- **Licensing page:** wording discrepancy between fetches — "advises of" vs. "advises on" corporate transactions.
- **People:** Surain Satgunarajah is named with a title on the Home page but has a 404 individual profile page and does not appear on the Practitioners overview page — no biography exists in any crawled source; current employment status unconfirmed.
- **People:** no email address or phone number is stated for any of the 9 core team members on either the Practitioners page or their individual profile pages.
- **People:** several staff mentioned only in Case Studies feature articles (Wan Nurul Aisyah, Noorserra Aryecca Armat, Dr Kumutha Priya, Chien Nee Yew, Jayavaruman Subramaniam, Kazuki Ishigami) have no current profile page or Practitioners-page listing; their current status at the firm is unconfirmed from live content.
- **Contact information:** the branch-office street name conflicts between an internal working assumption supplied for this task ("Jalan Medini Utama 1") and the live Contacts page, re-verified twice ("Jalan Medini Utara 1"); the live page text (Utara) was used as the recorded value.
- **Contact information:** the HQ suite listing conflicts between the current Contacts page (suites A-16-5 & A-16-6) and a 2017-dated firm announcement (adds suite A-33-3A) — not resolved; may reflect a since-vacated expansion suite.
- **Contact information:** a second email domain ("info@adipven.edu.my") appears once, in Home-page Terms & Conditions boilerplate, conflicting with the primary Contacts-page email ("info@adipven.com"), which is treated as authoritative.
- **Certifications:** the Home page's ISO 9001:2015/UKAS and "Eco-Office" claims are directly evidenced only by image filenames on that page, but are corroborated by verbatim text in two Case Studies entries ("ISO 9001-2015 Registration Announcement" and "Women Scientists in Patenting"); no certificate number, accrediting-body contact, or validity date is given anywhere in crawled content.
- **Founding date:** no founding date appears on the About Us page itself; "2 January 2012" is sourced only from the "Adipven is Expanding" Case Studies announcement, and is broadly consistent with (but not independently confirmed by) the "New Year Wishes" announcement's "five years" reference.
- **Case Studies:** the source list for this content type contained 35 distinct URLs (the working assumption going in was "34" — a minor miscount, not a missing/extra page).
- **Case Studies:** no publication date is displayed on the live page for any of the 35 entries; where a date is recorded above, it was inferred from in-text references (e.g., a cited judgment date) and is flagged as such, not treated as a confirmed publication date.
- **Case Studies:** "Asia IP PPH Story" links to an external article whose content was not retrievable — flagged `[TRUNCATED IN SOURCE]`.
- **Case Studies:** "Malaysia: Jurisdiction of Court is Defined" does not name the specific parties on the source page.
- **Case Studies:** "Malaysia: A Copyright Saga" contains an apparently malformed currency figure ("USD27,6073.00"), reproduced exactly as extracted rather than corrected.
- **Case Studies:** "Malaysia: Who Owns the Bike?" contains an ambiguous sentence as to which suit/defendant a damages dismissal applied to; reproduced as extracted with an inline uncertainty flag.
- **Case Studies:** three pairs of entries describe overlapping/related litigation from separate source pages (the two Merck Sharp & Dohme v Hovid pages; the two JLLP/Jones Lang Wootton v Singham Sulaiman pages; the two Ho Shen Lee v TNL Plastic Manufacturer pages) — per extraction rules, each pair is recorded as two independent entries reflecting each source page's own framing, cross-referenced rather than merged.
- All content in this document was obtained via an automated fetch-and-convert process (page HTML converted to markdown by a fetch tool) rather than direct raw-HTML transcription; wording was instructed to be preserved verbatim and summarization avoided, but character-level fidelity for longer passages could not be independently re-verified against raw HTML in every instance. Passages explicitly marked as paraphrased/inconsistent are flagged inline as noted above.

### Conflicting information found

- Norlela Mat Lias: title "Director, Intellectual Property Services" (Practitioners page) vs. "Director, Intellectual Property Services (I)" (individual profile page).
- Mohd Faizul Mohd Yin: title "Director, IP Services II" (Practitioners page, individual profile page, Home page) vs. "Director, Intellectual Property Services" without the "(II)" suffix (Appointment page).
- Nur Amalina Zamani: credential stated as "Registered Malaysian New Plant Variety and Grant of Breeder's Right Agent" only (Practitioners page) vs. additionally "Registered Malaysian Trademark ... Agent (Registration No. MYA/2024/0077)" (individual profile page).
- Dr. Soon Wei Chook: patent co-invention described with specific subject matter ("two patented methods... silver nanomaterials and photocatalytic wastewater treatment," individual profile page) vs. generically ("co-invented patented items in Malaysia," Practitioners page).
- Branch office street: "Jalan Medini Utara 1" (live Contacts page, verified twice) vs. "Jalan Medini Utama 1" (a prior/assumed value supplied as task background, not corroborated by the live site).
- HQ suite listing: current Contacts page (A-16-5 & A-16-6) vs. 2017 firm announcement (A-16-5, A-16-6 & A-33-3A).
- Contact email: "info@adipven.com" (Contacts page; also used as sign-off on multiple firm announcements) vs. "info@adipven.edu.my" (appears once, in Home-page legal boilerplate).
- Services overview page (`/services/`): whether a practitioner-name list and service-category bullet list are core body content (one fetch) or repeating nav/widget chrome (a verbatim-reproduction fetch).
- Licensing page: "advises of corporate transactions" vs. "advises on corporate transactions."

### Content deliberately excluded

- Navigation menus, breadcrumb links (e.g., "Home | Services"), and repeated masthead/logo text present on every crawled page.
- Cookie/consent banner and privacy-management dialog text, present on every crawled page.
- Chatbot widget UI text ("Ask Frank for Help" and its associated inline contact-request form), present site-wide.
- PayPal donation/payment link chrome (distinct from the one substantive mention of a PayPal payment facility recorded under Pricing & Commercial Terms, which came from a firm announcement's own body text, not link chrome).
- WhatsApp contact-widget chrome.
- "Recent Posts" and similar sidebar/related-content widgets on individual lawyer profile pages and elsewhere.
- Non-informational image alt text and CSS/JS/tracking artifacts.
- Terms & Conditions / privacy-policy legal boilerplate about cookies and the Malaysian Personal Data Protection Act 2010, repeated across pages (recorded once, generically, under Credentials, Certifications & Compliance, rather than per-page).
- The entire News section (~250 blog-post articles and the `/news/`, `/news-2/` landing pages) — excluded per explicit user instruction; see `00-index.md` for the sitemap reference.
- Orphaned WordPress theme/demo pages not linked from live navigation: `/sample-page/`, `/sample-page-2/`, `/typography/`, `/homepage/`, `/homepage-3/`, `/homepage-5/`, `/landing/`, `/practices/` (duplicate of `/services/` with unverified generic law-firm stats inconsistent with the rest of the site), the orphaned stub `/ramakrishna-damodharan/` (no content, duplicate of the canonical `/lawyer/ramakrishna-damodharan/`), and the pure auto-generated `/lawyer/` team archive index page. See `00-index.md` for full reasoning per page.
- `/videos/` — contains no actual video content, descriptions, or media; page is navigation/chatbot/cookie boilerplate only.
- "LEGAL AWARDS" section on the Appointment page — contained only image placeholders with no accompanying text.

### Recommended follow-up sources

- To resolve the branch-address and HQ-suite conflicts, and the two contact-email domains, a direct request to Adipven for current official contact details would be more reliable than the live-site text alone.
- To confirm the ISO 9001:2015 and Eco-Office certification claims with certificate-level detail (certifying body, certificate number, validity date), a certificate document or direct confirmation from the firm (or from UKAS, if that is indeed the accrediting body suggested by the homepage image filename) would be needed — the website text alone only confirms the claim was made, not independently verified.
- To fill the biographical gap for Surain Satgunarajah, and confirm current employment status for the six individuals named only in Case Studies feature articles (Wan Nurul Aisyah, Noorserra Aryecca Armat, Dr Kumutha Priya, Chien Nee Yew, Jayavaruman Subramaniam, Kazuki Ishigami), direct confirmation from the firm would be needed, since no current live page addresses them.
- Pricing/fee information (entirely absent from the crawled site) would need to come directly from the firm, e.g. via a quote request, if required for the knowledge base's intended use case.
