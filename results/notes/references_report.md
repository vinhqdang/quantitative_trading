# Verification report: references.bib (40 entries)

Checked 2026-10-11. Output: `references_verified.bib` (same 40 keys, same order). The original `references.bib` was not modified.

Sources used: Crossref `api.crossref.org/works/<doi>` (DOI records, and title/author search for DOI-less items); arXiv API (`export.arxiv.org`); publisher or proceedings pages (USENIX Security 2019 page, NeurIPS 2017 proceedings page, Frontiers article page, AAAI-hosted ICML 2003 paper PDF); OpenAlex, RePEc (IDEAS) and Semantic Scholar where Crossref lacked given names or pages.

Totals: **32 VERIFIED, 6 CHANGED, 2 UNVERIFIED** (2 UNVERIFIED entries are verified apart from the page range).

## Per-key status

- becker1968: VERIFIED (Crossref 10.1086/259394). DOI and issue 2 added.
- polinsky2000: VERIFIED (Crossref 10.1257/jel.38.1.45). DOI and issue 1 added; authors are A. Mitchell Polinsky and Steven Shavell.
- aggarwal2006: CHANGED (Crossref 10.1086/503652). Journal is "The Journal of Business" (old: "Journal of Business"). Footnote asterisk removed from title. Given names added. First author matches.
- comerton2014: VERIFIED (Crossref 10.1093/rof/rfs040). Given names added. Crossref gives online 2013 and print 2014; 2014 kept because it is the volume year.
- khwaja2005: VERIFIED (Crossref 10.1016/j.jfineco.2004.06.014; given names from RePEc, ideas.repec.org/a/eee/jfinec/v78y2005i1p203-241.html). Crossref has only initials ("A KHWAJA", "A MIAN").
- wang2020: VERIFIED (Crossref 10.24963/ijcai.2020/638). Booktitle now the Crossref form; the "(IJCAI-20)" tag is not in the record.
- wang2018: VERIFIED (Crossref 10.24963/ijcai.2018/75). Booktitle now the Crossref form.
- cartea2020: VERIFIED (Crossref 10.1080/1350486X.2020.1726783). Given names added.
- leal2019: CHANGED (Crossref 10.1016/j.jebo.2017.04.013). Crossref splits the first author as given "Sandrine Jacob", family "Leal". The old file used surname "Jacob Leal". **Human check needed** (see below).
- zhang2016: VERIFIED (Crossref 10.1371/journal.pone.0160406). Five authors with full given names (old file had surnames only).
- zhao2020: VERIFIED (Crossref 10.3389/fphy.2020.00135). Article number 135. Given names added.
- byrd2020: VERIFIED (Crossref 10.1145/3384441.3395986). Pages 11--22 added; third author given as "Tucker Hybinette" (Crossref).
- vyetrenko2019: CHANGED. The arXiv preprint 1912.04941 (2019) has a published version: Proceedings of the First ACM International Conference on AI in Finance, 2020, DOI 10.1145/3383455.3422561 (Crossref). Type changed from @misc to @inproceedings; year 2019 changed to 2020; "Vyetrenko and others" replaced with the full author list (arXiv and Crossref). **Human check needed**: in-text year.
- platt2018: CHANGED. The arXiv preprint 1611.08510 has a journal version: Physica A 503 (2018) 1092--1106, DOI 10.1016/j.physa.2018.08.055 (Crossref). Type changed from @misc to @article.
- xu2019: VERIFIED (USENIX publisher page, usenix.org/conference/usenixsecurity19/presentation/xu-jiahua). No Crossref record; no DOI added. Authors Jiahua Xu and Benjamin Livshits.
- kamps2018: VERIFIED (Crossref 10.1186/s40163-018-0093-5). Issue 1 added; article number 18 kept as pages.
- lamorgia2020: VERIFIED (Crossref 10.1109/ICCCN49398.2020.9209660). Pages 1--9 added.
- lamorgia2023: VERIFIED (Crossref 10.1145/3561300).
- hu2022: CHANGED. The arXiv preprint 2204.12929 has a journal version: Proceedings of the ACM on Management of Data 1(1), 2023, DOI 10.1145/3588686 (Crossref). Same title and authors. Type changed from @misc to @article. The key stays hu2022 although the year is now 2023. **Human check needed**: in-text year.
- dhawan2023: VERIFIED (Crossref 10.1093/rof/rfac051).
- cong2023: VERIFIED (Crossref 10.1287/mnsc.2021.02709). Given name "Lin William".
- victor2021: VERIFIED (Crossref 10.1145/3442381.3449824). Booktitle is the Crossref form; the "(WWW '21)" tag from the old entry is not in the record and was dropped.
- palshikar2008: VERIFIED (Crossref 10.1007/s10618-007-0076-8).
- cao2016: VERIFIED (Crossref 10.1109/TNNLS.2015.2480959). Five authors with given names.
- sun2012: VERIFIED (Crossref 10.1371/journal.pone.0045598).
- jaeger2025: VERIFIED (arXiv 2512.18918). No journal version found in Crossref search. Kept as @misc with eprint.
- saavedra2011: VERIFIED (Crossref 10.1073/pnas.1018462108). DOI, issue 13 and pages added. The DOI was located by title search and confirmed by the DOI record.
- tuccella2021: VERIFIED (arXiv 2110.03687). Authors Jean-Noël Tuccella, Philip Nadler, Ovidiu Şerban. No journal version found. Kept as @misc.
- fabre2025: VERIFIED (arXiv 2504.15908). Only SSRN preprints found in Crossref; no journal version. Kept as @misc.
- liang2025: VERIFIED (arXiv 2512.17372). No journal version found. Kept as @misc.
- platkiewicz2017: VERIFIED (Crossref 10.1162/NECO_a_00927).
- amarasingham2012: VERIFIED (Crossref 10.1152/jn.00633.2011).
- grun2009: VERIFIED (Crossref 10.1152/jn.00093.2008).
- louis2010: VERIFIED. Title, volume and year from Crossref 10.3389/fncom.2010.00127. Authors from the Frontiers article page (Louis, Gerstein, Grün, Diesmann) and Semantic Scholar ("Sebastien G. R. Louis"). Article number 127 from OpenAlex. Crossref lists only the first author. **Human check needed**: the Frontiers metadata has "Sebastien G R" and lowercase "george L", normalised here to "Sebastien G. R." and "George L.".
- mcmahan2003: UNVERIFIED (pages). Authors (H. Brendan McMahan, Geoffrey J. Gordon, Avrim Blum), title and venue are confirmed by the ICML 2003 paper PDF hosted by AAAI (aaai.org/Papers/ICML/2003/ICML03-071.pdf) and the Semantic Scholar record of DBLP key conf/icml/McMahanGB03. Pages 536--543 come from the old entry; the PDF does not show them. Crossref has no record. The note field says so.
- lanctot2017: UNVERIFIED (pages). Authors (full names), title, volume 30 and year 2017 are confirmed by the NeurIPS 2017 proceedings abstract page (papers.nips.cc, 3323fe11e9595c09af38fe67567a9394). No page range was found, so none is written; the note field says so. Crossref has no record.
- avenhaus2002: VERIFIED (Crossref 10.1016/s1574-0005(02)03014-x). Pages 1947--1987; Handbook volume 3 confirmed by the container title. The "Chapter 51" prefix is dropped from the title. Book editors are not in the Crossref record and were not added.
- nguyen2017: VERIFIED (Crossref 10.1016/j.jimonfin.2017.02.028). Volume 74 added. Given name "Richard" as in Crossref (no middle name there).
- nguyen2023: CHANGED (Crossref 10.1108/JES-01-2023-0031). Year changed 2023 to 2024: Crossref gives print issue year 2024 for volume 51, issue 2 (online 2023). Title protected as "{COVID-19}" and "{Vietnam}". Given names added. **Human check needed**: in-text year.
- vo2023: VERIFIED (Crossref 10.1371/journal.pone.0285821). Volume 18, issue 5 and pages added; author format corrected to Family, Given; the "metadata checked" note removed.

## Differences from the old file (for the paper's in-text claims)

- Title: no substantive title difference for any key. Casing changed to the Crossref sentence case in several entries; vyetrenko2019 now carries the published title ("Get real: ...").
- First author: all match the real records except leal2019, where the old surname "Jacob Leal" differs from the record's family name "Leal".
- Year: vyetrenko2019 (2019 to 2020), hu2022 (year field 2023), nguyen2023 (2023 to 2024). In-text citations to these keys will change if the journal versions are cited.
- Type: vyetrenko2019 (misc to inproceedings), platt2018 (misc to article), hu2022 (misc to article).

## Needs the human's attention

1. leal2019: confirm the first author's family name (Leal vs Jacob Leal).
2. vyetrenko2019, hu2022, nguyen2023: decide whether to cite the journal or conference version (year changed); update in-text citations.
3. platt2018: confirm the Physica A version is the one to cite.
4. mcmahan2003: confirm pages 536--543 against the ACM/ICML 2003 record.
5. lanctot2017: add the page range from the NeurIPS 2017 proceedings (none verified here).
6. avenhaus2002: add the book editors (APA requires them for chapters); not in Crossref.
7. louis2010: confirm author given names (Frontiers metadata has abbreviated forms); Crossref lists only the first author.
8. Entries with an arXiv record and no journal version found (jaeger2025, tuccella2021, fabre2025, liang2025): kept as preprints; confirm nothing newer has been published.
