"""Minimal drop-in FPDF replacement for Streamlit-in-Snowflake (no external deps).
Supports the subset of the FPDF API used by this project: add_page, set_font,
cell, multi_cell, ln, line, set_fill_color, set_text_color, set_draw_color,
set_auto_page_break, set_x, get_y, output.
"""

class FPDF:
    def __init__(self):
        self.w = 210  # A4 width mm
        self.h = 297  # A4 height mm
        self.pages = []
        self.current_page = -1
        self.x = 10
        self.y = 10
        self.font_family = "Helvetica"
        self.font_style = ""
        self.font_size = 12
        self.text_r, self.text_g, self.text_b = 0, 0, 0
        self.fill_r, self.fill_g, self.fill_b = 255, 255, 255
        self.draw_r, self.draw_g, self.draw_b = 0, 0, 0
        self.auto_page_break = True
        self.b_margin = 15
        self.objects = []
        self.fonts_used = set()
        self._page_contents = []

    def add_page(self):
        self.current_page += 1
        self._page_contents.append([])
        self.x = 10
        self.y = 10

    def set_auto_page_break(self, auto=True, margin=15):
        self.auto_page_break = auto
        self.b_margin = margin

    def set_font(self, family, style="", size=0):
        self.font_family = family
        self.font_style = style
        if size > 0:
            self.font_size = size
        base = family if family != "Helvetica" else "Helvetica"
        if "B" in style and "I" in style:
            self.fonts_used.add(f"{base}-BoldOblique")
        elif "B" in style:
            self.fonts_used.add(f"{base}-Bold")
        elif "I" in style:
            self.fonts_used.add(f"{base}-Oblique")
        else:
            self.fonts_used.add(base)

    def set_text_color(self, r, g=None, b=None):
        self.text_r = r
        self.text_g = g if g is not None else r
        self.text_b = b if b is not None else r

    def set_fill_color(self, r, g=None, b=None):
        self.fill_r = r
        self.fill_g = g if g is not None else r
        self.fill_b = b if b is not None else r

    def set_draw_color(self, r, g=None, b=None):
        self.draw_r = r
        self.draw_g = g if g is not None else r
        self.draw_b = b if b is not None else r

    def set_x(self, x):
        self.x = x

    def get_y(self):
        return self.y

    def _check_page_break(self, h):
        if self.auto_page_break and self.y + h > self.h - self.b_margin:
            self.add_page()

    def _char_width(self):
        return self.font_size * 0.5

    def _get_font_name(self):
        base = self.font_family if self.font_family != "Helvetica" else "Helvetica"
        if "B" in self.font_style and "I" in self.font_style:
            return f"{base}-BoldOblique"
        elif "B" in self.font_style:
            return f"{base}-Bold"
        elif "I" in self.font_style:
            return f"{base}-Oblique"
        return base

    def _pdf_escape(self, s):
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _encode_text(self, s):
        return s.encode("latin-1", errors="replace").decode("latin-1")

    def cell(self, w, h=5, txt="", ln=False, align="L", fill=False):
        self._check_page_break(h)
        txt = self._encode_text(str(txt))
        cmd = []
        if fill:
            cmd.append(f"{self.fill_r/255:.3f} {self.fill_g/255:.3f} {self.fill_b/255:.3f} rg")
            x_pt = self.x * 72 / 25.4
            y_pt = (self.h - self.y) * 72 / 25.4
            w_pt = w * 72 / 25.4
            h_pt = h * 72 / 25.4
            cmd.append(f"{x_pt:.2f} {y_pt - h_pt:.2f} {w_pt:.2f} {h_pt:.2f} re f")
        cmd.append(f"BT")
        cmd.append(f"/{self._get_font_name()} {self.font_size} Tf")
        cmd.append(f"{self.text_r/255:.3f} {self.text_g/255:.3f} {self.text_b/255:.3f} rg")
        text_y = (self.h - self.y - h * 0.7) * 72 / 25.4
        if align == "C":
            text_w = len(txt) * self.font_size * 0.4
            text_x = (self.x + (w - text_w / (72/25.4)) / 2) * 72 / 25.4
        elif align == "R":
            text_w = len(txt) * self.font_size * 0.4
            text_x = (self.x + w - text_w / (72/25.4) - 1) * 72 / 25.4
        else:
            text_x = (self.x + 1) * 72 / 25.4
        cmd.append(f"{text_x:.2f} {text_y:.2f} Td")
        cmd.append(f"({self._pdf_escape(txt)}) Tj")
        cmd.append("ET")
        if self.current_page >= 0:
            self._page_contents[self.current_page].extend(cmd)
        if ln:
            self.y += h
            self.x = 10
        else:
            self.x += w

    def multi_cell(self, w, h, txt):
        txt = self._encode_text(str(txt))
        cw = self.font_size * 0.42 * 25.4 / 72
        max_chars = max(int(w / cw), 1)
        words = txt.split(" ")
        line = ""
        for word in words:
            test = f"{line} {word}".strip() if line else word
            if len(test) > max_chars and line:
                self.cell(w, h, line, ln=True)
                line = word
            else:
                line = test
        if line:
            self.cell(w, h, line, ln=True)

    def ln(self, h=None):
        if h is None:
            h = self.font_size * 25.4 / 72
        self.y += h
        self.x = 10

    def line(self, x1, y1, x2, y2):
        cmd = []
        cmd.append(f"{self.draw_r/255:.3f} {self.draw_g/255:.3f} {self.draw_b/255:.3f} RG")
        x1_pt = x1 * 72 / 25.4
        y1_pt = (self.h - y1) * 72 / 25.4
        x2_pt = x2 * 72 / 25.4
        y2_pt = (self.h - y2) * 72 / 25.4
        cmd.append(f"{x1_pt:.2f} {y1_pt:.2f} m {x2_pt:.2f} {y2_pt:.2f} l S")
        if self.current_page >= 0:
            self._page_contents[self.current_page].extend(cmd)

    def output(self):
        font_map = {
            "Helvetica": "Helvetica",
            "Helvetica-Bold": "Helvetica-Bold",
            "Helvetica-Oblique": "Helvetica-Oblique",
            "Helvetica-BoldOblique": "Helvetica-BoldOblique",
        }
        used = sorted(self.fonts_used) if self.fonts_used else ["Helvetica"]
        obj_offsets = []
        buf = b"%PDF-1.4\n"

        obj_num = 1
        # Catalog
        obj_offsets.append(len(buf))
        buf += f"{obj_num} 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n".encode()
        obj_num += 1

        # Pages placeholder - will know page count
        pages_obj = obj_num
        obj_offsets.append(len(buf))
        kids = " ".join(f"{pages_obj + 1 + len(used) + i} 0 R" for i in range(len(self._page_contents)))
        buf += f"{obj_num} 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(self._page_contents)} >>\nendobj\n".encode()
        obj_num += 1

        # Font objects
        font_obj_map = {}
        for fname in used:
            obj_offsets.append(len(buf))
            pdf_name = font_map.get(fname, "Helvetica")
            buf += f"{obj_num} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /{pdf_name} /Encoding /WinAnsiEncoding >>\nendobj\n".encode()
            font_obj_map[fname] = obj_num
            obj_num += 1

        # Font resource dict
        font_refs = " ".join(f"/{fname} {font_obj_map[fname]} 0 R" for fname in used)
        resources = f"<< /Font << {font_refs} >> >>"

        # Page objects + content streams
        for page_cmds in self._page_contents:
            # Content stream
            content_obj = obj_num
            obj_offsets.append(len(buf))
            stream_data = "\n".join(page_cmds)
            stream_bytes = stream_data.encode("latin-1", errors="replace")
            buf += f"{obj_num} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode()
            buf += stream_bytes
            buf += b"\nendstream\nendobj\n"
            obj_num += 1

            # Page object
            obj_offsets.append(len(buf))
            w_pt = 210 * 72 / 25.4
            h_pt = 297 * 72 / 25.4
            buf += f"{obj_num} 0 obj\n<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 {w_pt:.2f} {h_pt:.2f}] /Contents {content_obj} 0 R /Resources {resources} >>\nendobj\n".encode()
            obj_num += 1

        # Cross-reference table
        xref_pos = len(buf)
        buf += b"xref\n"
        buf += f"0 {obj_num}\n".encode()
        buf += b"0000000000 65535 f \n"
        for offset in obj_offsets:
            buf += f"{offset:010d} 00000 n \n".encode()

        buf += b"trailer\n"
        buf += f"<< /Size {obj_num} /Root 1 0 R >>\n".encode()
        buf += b"startxref\n"
        buf += f"{xref_pos}\n".encode()
        buf += b"%%EOF\n"
        return buf
