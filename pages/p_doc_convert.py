import streamlit as st
import os
from pathlib import Path
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, confidentiality_notice, section

api_key = setup_page()
slim_header("🔄", "Convert & Process", "PDF to Word, Word to PDF, merge PDFs, and document reconstruction")
confidentiality_notice()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 PDF / Image → Word",
    "🔄 Word → PDF",
    "📚 Merge PDFs",
    "✂️ Split PDF",
    "🗜️ Compress PDF",
])


# ── Tab 1: PDF / Image → Word ─────────────────────────────────────
with tab1:
    st.markdown("Upload a scanned PDF or image — Claude Opus 4.7 reads every page and produces an editable Word document.")

    doc_type = st.selectbox("Document type", [
        "legal", "contract", "court_filing", "deed", "invoice", "report", "letter", "general",
    ], key="conv_doctype")
    uploaded_file = st.file_uploader(
        "Drop your scanned PDF or image",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
        key="conv_upload",
    )
    if uploaded_file:
        st.caption(f"📄 {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB")

    if st.button("🚀 Convert to Word", type="primary",
                 disabled=not (uploaded_file and api_key), use_container_width=True):
        from utils.claude_processor import ClaudeDocumentProcessor
        from utils.document_builder import DocumentBuilder
        from utils.confidentiality import ConfidentialityManager
        cm = ConfidentialityManager()
        try:
            tmp_in = cm.secure_path(uploaded_file.name)
            with open(tmp_in, "wb") as f:
                f.write(uploaded_file.getbuffer())

            bar = st.progress(0, text="Reading document…")
            extracted = ClaudeDocumentProcessor(api_key).process_document(tmp_in, doc_type)
            bar.progress(80, text="Building Word file…")

            output_name = Path(uploaded_file.name).stem + "_reconstructed.docx"
            output_path = cm.secure_path(output_name)
            DocumentBuilder().build_word_document(extracted, uploaded_file.name, output_path)
            bar.progress(100, text="Done!")

            with open(output_path, "rb") as f:
                docx_bytes = f.read()
            st.session_state.conv_docx_bytes = docx_bytes
            st.session_state.conv_output_name = output_name
            st.session_state.last_audit = cm.get_audit_report()
        except Exception as exc:
            st.error(f"Conversion failed: {exc}")

    if st.session_state.get("conv_docx_bytes"):
        st.success("✅ Ready to download!")
        st.download_button(
            "📥 Download Word (.docx)",
            data=st.session_state.conv_docx_bytes,
            file_name=st.session_state.conv_output_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="conv_dl",
        )
        if st.button("🔄 Convert another file", key="conv_reset"):
            st.session_state.pop("conv_docx_bytes", None)
            st.session_state.pop("conv_output_name", None)
            st.rerun()


# ── Tab 2: Word → PDF ─────────────────────────────────────────────
with tab2:
    section("🔄 Convert Word Document to PDF")
    wl, wr = st.columns(2, gap="large")
    with wl:
        word_file = st.file_uploader("Upload Word Document (.docx)", type=["docx"], key="w2p_up")
        if word_file:
            st.info(f"📝 **{word_file.name}** · {word_file.size / 1024:.1f} KB")
            if st.button("🔄 Convert to PDF", type="primary", use_container_width=True, key="w2p_btn"):
                from utils.word_to_pdf import convert_word_to_pdf
                from utils.confidentiality import ConfidentialityManager
                try:
                    cm = ConfidentialityManager()
                    docx_path = cm.secure_path(word_file.name)
                    with open(docx_path, "wb") as f:
                        f.write(word_file.getbuffer())
                    pdf_name = Path(word_file.name).stem + ".pdf"
                    pdf_path = cm.secure_path(pdf_name)
                    with st.spinner("Converting…"):
                        convert_word_to_pdf(docx_path, pdf_path)
                    st.session_state.w2p_pdf_path = pdf_path
                    st.session_state.w2p_pdf_name = pdf_name
                    st.success("✅ Done!")
                except Exception as exc:
                    st.error(f"Failed: {exc}")
    with wr:
        section("Download")
        if st.session_state.get("w2p_pdf_path") and os.path.exists(st.session_state.w2p_pdf_path):
            with open(st.session_state.w2p_pdf_path, "rb") as f:
                st.download_button("📥 Download PDF", data=f.read(),
                    file_name=st.session_state.w2p_pdf_name, mime="application/pdf",
                    use_container_width=True)
        else:
            st.markdown('<div class="empty-list">Your PDF will appear here after conversion.</div>',
                        unsafe_allow_html=True)


# ── Tab 3: Merge PDFs ─────────────────────────────────────────────
with tab3:
    section("📚 Merge PDFs into a Court Bundle")
    pdfs = st.file_uploader("Upload PDFs to merge", type=["pdf"], accept_multiple_files=True, key="merge_up")
    if pdfs:
        st.info(f"📄 {len(pdfs)} file(s) ready")
        titles = []
        cols = st.columns(2)
        for i, pdf in enumerate(pdfs):
            title = cols[i % 2].text_input(f"Title for '{pdf.name}'",
                value=pdf.name.replace(".pdf", ""), key=f"mt_{i}")
            titles.append(title)
        if st.button("📚 Merge & Download Bundle", type="primary", key="merge_btn"):
            try:
                import PyPDF2
                from utils.confidentiality import ConfidentialityManager
                cm = ConfidentialityManager()
                merger = PyPDF2.PdfMerger()
                for pdf, title in zip(pdfs, titles):
                    path = cm.secure_path(pdf.name)
                    with open(path, "wb") as f:
                        f.write(pdf.getbuffer())
                    merger.append(path, outline_item=title)
                out_path = cm.secure_path("court_bundle.pdf")
                merger.write(out_path)
                merger.close()
                with open(out_path, "rb") as f:
                    st.download_button("📥 Download Court Bundle", f.read(),
                        "court_bundle.pdf", "application/pdf")
                st.success(f"✅ Bundle ready: {len(pdfs)} documents merged")
            except Exception as exc:
                st.error(f"Merge failed: {exc}")
    else:
        st.markdown('<div class="empty-list">Upload at least two PDFs to merge.</div>',
                    unsafe_allow_html=True)


# ── Tab 4: Split PDF ──────────────────────────────────────────────
with tab4:
    section("✂️ Split / Extract Pages from PDF")
    import io as _io
    sp_file = st.file_uploader("Upload PDF to split", type=["pdf"], key="sp_up")
    if sp_file:
        try:
            import fitz as _fitz
            sp_doc = _fitz.open(stream=sp_file.getbuffer(), filetype="pdf")
            total_pages = len(sp_doc)
            st.info(f"📄 **{sp_file.name}** · {total_pages} pages · {sp_file.size / 1024:.1f} KB")
            sp_doc.close()

            sp_mode = st.radio("Split Mode", ["Extract page range", "Split into individual pages",
                                               "Split into equal parts"], horizontal=True, key="sp_mode")
            if sp_mode == "Extract page range":
                c1, c2 = st.columns(2)
                sp_from = c1.number_input("From page", min_value=1, max_value=total_pages, value=1, key="sp_from")
                sp_to   = c2.number_input("To page",   min_value=1, max_value=total_pages, value=min(total_pages, 5), key="sp_to")
                sp_name = st.text_input("Output filename", value="extracted_pages.pdf", key="sp_name")
                if st.button("✂️ Extract Pages", type="primary", key="sp_btn_range"):
                    sp_doc2 = _fitz.open(stream=sp_file.getbuffer(), filetype="pdf")
                    out_doc = _fitz.open()
                    out_doc.insert_pdf(sp_doc2, from_page=int(sp_from)-1, to_page=int(sp_to)-1)
                    buf = _io.BytesIO()
                    out_doc.save(buf)
                    sp_doc2.close()
                    out_doc.close()
                    st.download_button("📥 Download Extracted Pages", buf.getvalue(),
                                       sp_name, "application/pdf", use_container_width=True, key="sp_dl_range")
                    st.success(f"✅ Pages {sp_from}–{sp_to} extracted ({int(sp_to)-int(sp_from)+1} pages)")

            elif sp_mode == "Split into individual pages":
                st.info(f"This will create {total_pages} separate PDF files, bundled in a ZIP.")
                if st.button("✂️ Split into Pages", type="primary", key="sp_btn_all"):
                    import zipfile as _zf
                    sp_doc3 = _fitz.open(stream=sp_file.getbuffer(), filetype="pdf")
                    zip_buf = _io.BytesIO()
                    with _zf.ZipFile(zip_buf, "w", _zf.ZIP_DEFLATED) as zf:
                        for i in range(total_pages):
                            pg_doc = _fitz.open()
                            pg_doc.insert_pdf(sp_doc3, from_page=i, to_page=i)
                            pg_buf = _io.BytesIO()
                            pg_doc.save(pg_buf)
                            pg_doc.close()
                            zf.writestr(f"page_{i+1:04d}.pdf", pg_buf.getvalue())
                    sp_doc3.close()
                    st.download_button("📥 Download ZIP (all pages)", zip_buf.getvalue(),
                                       "split_pages.zip", "application/zip", use_container_width=True, key="sp_dl_all")
                    st.success(f"✅ {total_pages} pages split")

            else:  # Equal parts
                n_parts = st.number_input("Number of equal parts", min_value=2,
                                          max_value=total_pages, value=2, key="sp_parts")
                if st.button("✂️ Split into Parts", type="primary", key="sp_btn_parts"):
                    import zipfile as _zf
                    import math as _math
                    sp_doc4 = _fitz.open(stream=sp_file.getbuffer(), filetype="pdf")
                    pages_per_part = _math.ceil(total_pages / int(n_parts))
                    zip_buf2 = _io.BytesIO()
                    with _zf.ZipFile(zip_buf2, "w", _zf.ZIP_DEFLATED) as zf:
                        for p in range(int(n_parts)):
                            start = p * pages_per_part
                            end   = min(start + pages_per_part - 1, total_pages - 1)
                            if start > total_pages - 1:
                                break
                            pt_doc = _fitz.open()
                            pt_doc.insert_pdf(sp_doc4, from_page=start, to_page=end)
                            pt_buf = _io.BytesIO()
                            pt_doc.save(pt_buf)
                            pt_doc.close()
                            zf.writestr(f"part_{p+1}_pages_{start+1}-{end+1}.pdf", pt_buf.getvalue())
                    sp_doc4.close()
                    st.download_button("📥 Download ZIP (all parts)", zip_buf2.getvalue(),
                                       "split_parts.zip", "application/zip", use_container_width=True, key="sp_dl_parts")
                    st.success(f"✅ Split into {n_parts} parts")
        except Exception as exc:
            st.error(f"Error: {exc}")
    else:
        st.markdown('<div class="empty-list">Upload a PDF to split it.</div>', unsafe_allow_html=True)


# ── Tab 5: Compress PDF ───────────────────────────────────────────
with tab5:
    section("🗜️ Compress PDF")
    import io as _io2
    cmp_file = st.file_uploader("Upload PDF to compress", type=["pdf"], key="cmp_up")
    if cmp_file:
        original_size = len(cmp_file.getbuffer())
        st.info(f"📄 **{cmp_file.name}** · Original size: {original_size / 1024:.1f} KB")
        compression_level = st.radio("Compression Level",
                                     ["Light (best quality)", "Medium (balanced)", "Aggressive (smallest file)"],
                                     horizontal=True, key="cmp_level")
        if st.button("🗜️ Compress PDF", type="primary", key="cmp_btn"):
            try:
                import fitz as _fitz2
                doc = _fitz2.open(stream=cmp_file.getbuffer(), filetype="pdf")
                buf = _io2.BytesIO()
                garbage_level = {"Light (best quality)": 1,
                                  "Medium (balanced)": 3,
                                  "Aggressive (smallest file)": 4}[compression_level]
                doc.save(buf, deflate=True, garbage=garbage_level, clean=True,
                         deflate_images=True, deflate_fonts=True)
                doc.close()
                compressed_size = len(buf.getvalue())
                saved_pct = (1 - compressed_size / original_size) * 100

                c1, c2, c3 = st.columns(3)
                c1.metric("Original Size",    f"{original_size / 1024:.1f} KB")
                c2.metric("Compressed Size",  f"{compressed_size / 1024:.1f} KB")
                c3.metric("Size Reduction",   f"{max(0, saved_pct):.1f}%",
                          delta=f"−{(original_size - compressed_size) / 1024:.1f} KB")

                out_name = cmp_file.name.replace(".pdf", "_compressed.pdf")
                st.download_button("📥 Download Compressed PDF", buf.getvalue(),
                                   out_name, "application/pdf", use_container_width=True, key="cmp_dl")
                if saved_pct < 5:
                    st.info("ℹ️ PDF was already well-optimised — minimal reduction possible.")
                else:
                    st.success(f"✅ Compressed by {saved_pct:.1f}% ({original_size//1024}KB → {compressed_size//1024}KB)")
            except Exception as exc:
                st.error(f"Compression failed: {exc}")
    else:
        st.markdown('<div class="empty-list">Upload a PDF to compress it.</div>', unsafe_allow_html=True)
