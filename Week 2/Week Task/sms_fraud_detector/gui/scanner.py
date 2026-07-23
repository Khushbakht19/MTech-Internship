"""
gui/scanner.py
---------------
The SMS Scanner page: the core interactive feature of the application.

The user pastes or types an SMS message, clicks "Scan Message", and the
trained Naive Bayes classifier (ml/classifier.py) returns:
    - A Spam / Legitimate verdict
    - A confidence score
    - Any suspicious keywords found inside the message

Every scan is saved into the prediction_history table so it shows up
on the Dashboard and the Prediction History page.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config


# A few ready-made examples so the user (or a grader) can test the
# scanner instantly without having to think up a message first.
EXAMPLE_MESSAGES = [
    "Congratulations! You have WON a $1000 gift card. Click here to claim now: bit.ly/claim-prize",
    "Hey, are we still meeting for lunch tomorrow at 1pm?",
    "URGENT: Your bank account has been suspended. Verify your details immediately at secure-bank-update.com",
]


class ScannerPage(tk.Frame):
    """The SMS Scanner page."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app
        self._example_index = 0

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_page_title()
        self._build_main_content()

    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="SMS Scanner", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="Paste an SMS message below to check whether it is spam or legitimate",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    def _build_main_content(self):
        content_row = tk.Frame(self, bg=config.COLORS["main_bg"])
        content_row.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        content_row.grid_rowconfigure(0, weight=1)
        content_row.grid_columnconfigure(0, weight=1, uniform="col")
        content_row.grid_columnconfigure(1, weight=1, uniform="col")

        self._build_input_card(content_row)
        self._build_result_card(content_row)

    # ------------------------------------------------------------------
    # INPUT CARD
    # ------------------------------------------------------------------
    def _build_input_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        header = tk.Label(
            card, text="Enter SMS Message", font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        text_container = tk.Frame(card, bg=config.COLORS["main_bg"], highlightthickness=1,
                                   highlightbackground=config.COLORS["border"])
        text_container.pack(fill="both", expand=True, padx=20)

        self.message_text = tk.Text(
            text_container, wrap="word", font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
            relief="flat", padx=12, pady=12, height=10,
            insertbackground=config.COLORS["text_primary"],
        )
        self.message_text.pack(fill="both", expand=True)
        self.message_text.bind("<KeyRelease>", self._update_char_count)

        self.char_count_label = tk.Label(
            card, text="0 characters", font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        self.char_count_label.pack(anchor="e", padx=20, pady=(6, 16))

        button_row = tk.Frame(card, bg=config.COLORS["card_bg"])
        button_row.pack(fill="x", padx=20, pady=(0, 20))

        scan_button = tk.Button(
            button_row, text="🔍  Scan Message", font=config.FONTS["button"],
            bg=config.COLORS["blue"], fg=config.COLORS["white"],
            activebackground=config.COLORS["blue"], activeforeground=config.COLORS["white"],
            relief="flat", cursor="hand2", padx=18, pady=10,
            command=self._handle_scan,
        )
        scan_button.pack(side="left")

        clear_button = tk.Button(
            button_row, text="Clear", font=config.FONTS["button"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
            activebackground=config.COLORS["main_bg"], activeforeground=config.COLORS["text_primary"],
            relief="flat", cursor="hand2", padx=18, pady=10,
            command=self._handle_clear,
        )
        clear_button.pack(side="left", padx=(10, 0))

        example_button = tk.Button(
            button_row, text="Try an Example", font=config.FONTS["button"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["blue"],
            activebackground=config.COLORS["card_bg"], activeforeground=config.COLORS["blue"],
            relief="flat", cursor="hand2", padx=18, pady=10,
            command=self._handle_try_example,
        )
        example_button.pack(side="right")

    def _update_char_count(self, event=None):
        text_content = self.message_text.get("1.0", "end-1c")
        self.char_count_label.config(text=f"{len(text_content)} characters")

    def _handle_clear(self):
        self.message_text.delete("1.0", "end")
        self._update_char_count()
        self._show_empty_result_state()

    def _handle_try_example(self):
        self.message_text.delete("1.0", "end")
        self.message_text.insert("1.0", EXAMPLE_MESSAGES[self._example_index])
        self._example_index = (self._example_index + 1) % len(EXAMPLE_MESSAGES)
        self._update_char_count()

    # ------------------------------------------------------------------
    # RESULT CARD
    # ------------------------------------------------------------------
    def _build_result_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        header = tk.Label(
            card, text="Detection Result", font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=20, pady=(20, 10))

        self.result_body = tk.Frame(card, bg=config.COLORS["card_bg"])
        self.result_body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configure two custom progress bar styles (spam = red, safe = green).
        style = ttk.Style()
        style.configure(
            "Spam.Horizontal.TProgressbar",
            troughcolor=config.COLORS["red_light"], background=config.COLORS["red"],
        )
        style.configure(
            "Safe.Horizontal.TProgressbar",
            troughcolor=config.COLORS["green_light"], background=config.COLORS["green"],
        )

        self._show_empty_result_state()

    def _clear_result_body(self):
        for widget in self.result_body.winfo_children():
            widget.destroy()

    def _show_empty_result_state(self):
        self._clear_result_body()
        placeholder = tk.Label(
            self.result_body, text="🛡️\n\nScan a message to see the result here",
            font=config.FONTS["body"], justify="center",
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        placeholder.place(relx=0.5, rely=0.4, anchor="center")

    def _handle_scan(self):
        message_text = self.message_text.get("1.0", "end-1c").strip()

        if not message_text:
            messagebox.showwarning(
                "Empty Message", "Please enter an SMS message before scanning."
            )
            return

        result = self.classifier.predict(message_text)

        # Persist this prediction so it appears on the Dashboard and
        # the Prediction History page.
        self.database.insert_prediction(
            message_text=message_text,
            prediction=result["label"],
            confidence=result["confidence"],
            detected_keywords=result["keywords_string"],
        )

        self._render_result(message_text, result)

    def _render_result(self, message_text, result):
        self._clear_result_body()

        is_spam = result["label"] == config.LABEL_SPAM
        accent = config.COLORS["red"] if is_spam else config.COLORS["green"]
        accent_light = config.COLORS["red_light"] if is_spam else config.COLORS["green_light"]
        verdict_text = "🚫  SPAM DETECTED" if is_spam else "✅  LEGITIMATE MESSAGE"
        progress_style = "Spam.Horizontal.TProgressbar" if is_spam else "Safe.Horizontal.TProgressbar"

        # --- Verdict badge ---
        badge = tk.Frame(self.result_body, bg=accent_light)
        badge.pack(fill="x", pady=(0, 16))
        badge_label = tk.Label(
            badge, text=verdict_text, font=(config.FONT_FAMILY, 15, "bold"),
            bg=accent_light, fg=accent, pady=14,
        )
        badge_label.pack()

        # --- Confidence meter ---
        confidence_label = tk.Label(
            self.result_body, text=f"Confidence Score: {result['confidence']}%",
            font=config.FONTS["body_bold"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        confidence_label.pack(anchor="w")

        progress = ttk.Progressbar(
            self.result_body, style=progress_style, maximum=100,
            value=result["confidence"], length=100,
        )
        progress.pack(fill="x", pady=(6, 16))

        # --- Detected keywords ---
        keywords_title = tk.Label(
            self.result_body, text="Detected Keywords", font=config.FONTS["body_bold"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        keywords_title.pack(anchor="w")

        keywords_text = result["keywords_string"] if result["keywords"] else "No suspicious keywords found"
        keywords_label = tk.Label(
            self.result_body, text=keywords_text, font=config.FONTS["body"],
            bg=config.COLORS["card_bg"],
            fg=config.COLORS["red"] if result["keywords"] else config.COLORS["text_muted"],
            wraplength=380, justify="left",
        )
        keywords_label.pack(anchor="w", pady=(4, 16))

        # --- Scanned message preview ---
        preview_title = tk.Label(
            self.result_body, text="Scanned Message", font=config.FONTS["body_bold"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        preview_title.pack(anchor="w")

        preview_text = message_text if len(message_text) <= 160 else message_text[:157] + "..."
        preview_label = tk.Label(
            self.result_body, text=preview_text, font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_secondary"],
            wraplength=380, justify="left",
        )
        preview_label.pack(anchor="w", pady=(4, 16))

        saved_label = tk.Label(
            self.result_body, text="✔ Saved to Prediction History",
            font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        saved_label.pack(anchor="w")
