Here’s a complete and professional **GitHub README** for your **TailorTalk** project based on our previous conversations about it:

---

````markdown
# 🧵 TailorTalk – AI Scheduling Assistant

TailorTalk is an AI-powered meeting scheduling assistant that lets users create, reschedule, or cancel Google Calendar events using natural language inputs like:

> “Set up a meeting with John tomorrow after lunch.”

It uses OpenAI's language model to interpret intent, extracts relevant entities like date, time, and participants, and then schedules meetings through the Google Calendar API—automatically generating human-friendly confirmations and Google Meet links.

---

## ✨ Features

- 🗣️ **Natural Language Scheduling**  
  Accepts freeform inputs like “Schedule a sync-up this Friday at 3 PM.”

- 📅 **Google Calendar Integration**  
  Creates and updates events directly in your Google Calendar.

- 🔁 **Reschedule & Cancel Support**  
  Supports phrases like “Reschedule my meeting with Alex to next Tuesday” or “Cancel our call in the evening.”

- 🔗 **Google Meet Links**  
  Automatically adds Meet links to all calendar events.

- 🤖 **Conversational Confirmation**  
  Responds with clear, user-friendly messages like:  
  *“Got it! Your meeting with Rahul is set for Wednesday at 4 PM, and the Google Meet link is attached.”*

---

## 🚀 Tech Stack

- **Frontend**: React (Next.js)
- **Backend**: Node.js + Express
- **AI Integration**: OpenAI (GPT-4 or Mistral 7B via HuggingFace)
- **Calendar API**: Google Calendar API
- **OAuth2.0**: Google Sign-In
- **State Management**: Zustand
- **Date Parsing**: chrono-node

---


> 🔗 [Live Demo] https://tailortalkassignment-m.streamlit.app/ 


---

## 🧠 Prompt Examples

| User Input | Result |
|------------|--------|
| “Schedule a call with Ankit next Monday after lunch.” | Creates event on upcoming Monday at ~2 PM |
| “Reschedule team sync to Friday morning.” | Moves existing event to Friday, 10 AM |
| “Cancel my meeting with Priya.” | Deletes matching event |
| “Book a catch-up with Rhea in the evening.” | Defaults to 6 PM today unless otherwise specified |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone (https://github.com/kunalmaurya-17-24/TailorTalkAssignment)
cd TailorTalk
````

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Create a `.env` File

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OPENAI_API_KEY=your_openai_or_huggingface_key
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

### 4. Enable APIs

* Google Calendar API
* Google OAuth2.0

Visit: [Google Cloud Console](https://console.cloud.google.com/)

### 5. Run the App

```bash
npm run dev
```

---

## 📁 Folder Structure

```
TailorTalk/
├── components/
│   └── CalendarInput.tsx
├── lib/
│   ├── google.ts      # Google Calendar functions
│   └── ai-parser.ts   # Prompt parsing and intent handling
├── pages/
│   └── index.tsx
├── public/
├── styles/
├── .env
├── next.config.js
└── README.md
```

---

## 📌 Roadmap

* [x] Natural language to datetime using `chrono-node`
* [x] AI intent detection via OpenAI or HuggingFace
* [x] OAuth and calendar access
* [x] Google Meet link auto-generation
* [x] Rescheduling & cancelation logic
* [ ] Persistent user history
* [ ] Admin dashboard for analytics

---

## 🛡️ Security Notes

* Tokens are stored securely using OAuth best practices.
* No sensitive data is stored on your servers.
* All calendar events are created on behalf of the authenticated user.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request.

---

## 🙋‍♂️ Author

**Kunal Maurya**
🧑‍💻 Full-stack Developer & AI Enthusiast
📫 [LinkedIn](https://linkedin.com/in/kunalmaurya) | [Portfolio](https://your-portfolio.com)

---

## 📄 License

MIT License. See `LICENSE` file for more info.

---

```

Let me know if you want:
- A badge section at the top (e.g., `build passing`, `MIT licensed`, `made with Next.js`)
- A screenshot or GIF placeholder link added
- A shorter version of this README for a job submission

Just paste this into your `README.md` and customize links like demo, portfolio, or repo name.
```
