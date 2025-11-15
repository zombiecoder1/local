---
trigger: manual
---

-----

# 🤖 এজেন্ট প্রোটোকল টেমপ্লেট: **প্রজেক্ট নাম**

## ✅ প্রারম্ভিক সম্মতি এবং যাচাইকরণ (Initial Consent & Verification)

এই এজেন্ট (Agent: `[Agent Name]`) স্বেচ্ছায়, স্বজ্ঞানে এবং কোনো প্রকারের প্ররোচনা ব্যতীত প্রজেক্ট ডিরেক্টরিতে থাকা সকল ফাইল ফোল্ডার (বিশেষত `README.md` এবং `SYSTEM_LOCK.json`) যাচাই করে এই মর্মে সম্মতি জানাচ্ছে যে সে নিচে বর্ণিত কঠোর নিয়মাবলী মেনে চলতে প্রস্তুত। এই নিয়ম ভঙ্গ হলে, এজেন্ট সম্পূর্ণ দায়ভার গ্রহণ করবে এবং **Self-failure documentation** তৈরি করবে।

### ১. ব্যবহারকারী স্ট্যাটাস যাচাইকরণ (User Status Verification)

  - **উদ্দেশ্য:** ব্যবহারকারী একজন **পেইড সাবস্ক্রাইবার** কিনা তা যাচাই করা।
  - **পদ্ধতি:**
      - `SYSTEM_LOCK.json`-এ `user_status` ফিল্ডে `paid` আছে কিনা চেক করা।
      - যদি না থাকে, কাজটি প্রত্যাখ্যান করা এবং ব্যবহারকারীকে পরবর্তী পদক্ষেপের জন্য নির্দেশ দেওয়া।
  - **ফলাফল:** `[SUCCESS: Paid User / FAILURE: Non-Paid User]`

### ২. পরিবেশের উপযোগিতা যাচাইকরণ (Environment Suitability Check)

  - **উদ্দেশ্য:** বর্তমানে প্রজেক্ট ডিরেক্টরিতে কাজ শুরু করার জন্য পরিবেশ উপযুক্ত কিনা তা নিশ্চিত করা।
  - **পদ্ধতি:**
      - `README.md` এবং `SYSTEM_LOCK.json` এর প্রাথমিক রিড সফল হয়েছে কিনা যাচাই করা।
      - যদি সফল হয় তবে **কন্টিনিউ** করবে।
      - যদি না হয়, অন্য একজন দক্ষ এজেন্টকে সংযুক্ত করার জন্য অনুরোধ জানানো হবে।
  - **ফলাফল:** `[CONTINUE / REQUEST_HANDOVER]`

-----

## ⚠️ কঠোর নিয়মাবলী (Core Mandate)

### ১. এজেন্ট দায়িত্ব (Agent Responsibilities)

  - ✅ প্রতিটি কাজ শুরুর আগে **SYSTEM\_LOCK.json** ফাইলটি (বা সমতুল্য কনফিগারেশন ফাইল) অবশ্যই পড়তে হবে।
  - ✅ বর্তমান সিস্টেম ও প্রজেক্টের **status** (যা `README.md`-এ বর্ণিত) পুঙ্খানুপুঙ্খভাবে যাচাই করতে হবে।
  - ✅ প্রতিটি কাজ, পরিবর্তন, ও ভেরিফিকেশনের পর প্রোটোকল অনুযায়ী **signature** রাখা বাধ্যতামূলক।
  - ❌ প্রজেক্টের নথিতে (যেমন `README.md`, `SYSTEM_LOCK.json`) নির্দিষ্ট না করা কোনো ফাইল বা কনফিগারেশনে **Unauthorized file changes** নিষিদ্ধ।
  - ❌ অসম্পূর্ণ কাজকে সম্পন্ন বলে ঘোষণা করা বা ব্যবহারকারীকে **মিথ্যা আশ্বাস** দেওয়া কঠোরভাবে নিষিদ্ধ।

### ২. কাজ শুরুর Protocol (Workflow Protocol)

**ধাপ ১: Root README.md বিশ্লেষণ**

  - বর্তমান system status কি?
  - কোন features প্রস্তুত (`ready`)?
  - কোন features বাকি (`pending`)?
  - **যাচাই:** `[README_ANALYSIS_COMPLETE]`

**ধাপ ২: SYSTEM\_LOCK.json যাচাই ও নির্ভরতা পরীক্ষা**

  - সব প্রয়োজনীয় paths/ফাইল/ফোল্ডার (`paths`) আছে কিনা?
  - প্রয়োজনীয় Dependencies/লাইব্রেরি installed কিনা?
  - পোর্ট/রিসোর্স (`Ports/Resources`) ব্যবহারের জন্য মুক্ত আছে কিনা?
  - **যাচাই:** `[SYSTEM_LOCK_VERIFIED]`

**ধাপ ৩: যদি সব ঠিক থাকে**

  - → পরবর্তী কাজ শুরু করুন।
  - → প্রতিটি পদক্ষেপ **logs/session\_[SESSION\_ID].log** ফাইলে বিস্তারিতভাবে নথিভুক্ত করুন।
  - → কাজ শেষে **Signature** রাখুন।

**ধাপ ৪: যদি কোনো সমস্যা (Blocker) থাকে**

  - → ব্যবহারকারীকে সরাসরি **Clear blocker report** দিন।
  - → নিজে থেকে সমস্যা সমাধানের **চেষ্টা করবেন না** (শুধুমাত্র অনুমোদিত বাগ ফিক্স ছাড়া)।
  - → **Blocker Report:** `[Blocker details and recommended action]`

### ৩. Signature Format (বাধ্যতামূলক)

প্রতিটি কাজ complete করার পর JSON-এ এই ফরম্যাট ব্যবহার করা আবশ্যক:

```json
{
  "agent": "[Agent Name]",
  "provider": "[Provider Name]",
  "session_id": "[SESSION_ID_HERE]",
  "conversation_id": "[CONV_ID_HERE]",
  "timestamp": "[YYYY-MM-DDTHH:MM:SS]",
  "task": "Task description from user/README.md",
  "status": "completed/failed/blocker",
  "changes": ["file1.py modified", "new_folder/file2.json created"],
  "verification": "Command output, test result, or screenshot reference"
}
```

### ৪. নিষিদ্ধ কাজ (Prohibited Actions)

❌ `README.md`-এ বলা স্ট্যাটাসের বাইরে কোনো তথ্য/স্ট্যাটাস **assume** করা।
❌ `SYSTEM_LOCK.json` যাচাই না করে কাজ শুরু করা।
❌ **Test** না করে "কাজ হয়েছে" বলে দাবি করা।
❌ **Signature** ছাড়া কাজ জমা দেওয়া।
❌ ব্যবহারকারীকে **বিভ্রান্ত** করা বা অসম্পূর্ণ তথ্য দেওয়া।

### ৫. দায়বদ্ধতা ও স্ব-ব্যর্থতা রিপোর্ট (Accountability & Self-Failure Report)

  - **যদি Agent প্রোটোকল follow করে:** → সব ঠিক।
  - **যদি Agent প্রোটোকল break করে বা মিথ্যা verification দেয়:** → **সম্পূর্ণ দায়ভার এজেন্টের**। এজেন্টকে স্বয়ংক্রিয়ভাবে নিম্নলিখিত নামে একটি রিপোর্ট তৈরি করতে হবে:
      - **ফাইল:** `logs/SELF_FAILURE_REPORT_[TIMESTAMP].md`
      - **বিষয়বস্তু:** কোন নিয়ম ভাঙা হয়েছে, কেন ভাঙা হয়েছে, এবং এর ফলে সিস্টেমে কী প্রভাব পড়েছে তার বিশদ বিবরণ।

### ৬. Verification Mandate (বাধ্যতামূলক যাচাইকরণ)

**প্রতিটি কাজে নিম্নলিখিত চারটি ধাপ অনুসরণ করা আবশ্যক:**

1.  **Before:** Current status check (based on `README.md` and `SYSTEM_LOCK.json`).
2.  **During:** Step-by-step logging (`logs/session_[SESSION_ID].log`)-এ নথিভুক্তকরণ।
3.  **After:** Test করে পরিবর্তনগুলো **verify** করা।
4.  **Finally:** Signature দিয়ে কাজটি **complete** করা।

**No verification = No completion = Failure**

-----

## 📝 Logging Template (নথিভুক্তকরণ টেমপ্লেট)

**File:** `logs/session_[SESSION_ID].log`

**Format:**

```
=== Session Start ===
Agent: [Agent Name]
Provider: [Provider Name]
Session ID: [ID]
Conversation ID: [ID]
Started: [Timestamp]

=== Verification Check (Initial) ===
User Status: [Paid/Not Paid]
System Lock: [Verified/Failed]

=== Task Description ===
[User Task description]

=== Actions Log ===
[Step 1 - YYYY-MM-DDTHH:MM:SS] Action taken (e.g., Read fileX, Running test Y)
[Step 2 - YYYY-MM-DDTHH:MM:SS] Action taken
...

=== Verification Results ===
[Test command run and its output/Test results]

=== Signature ===
[JSON signature]

=== Session End ===
```