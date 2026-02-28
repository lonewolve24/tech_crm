# Quick Start: Technician Dashboard

## Access the Dashboard

1. **Log in** as a technician
   ```
   URL: http://localhost:8000/login/
   Email: tech_user@example.com (or your technician account)
   Password: Your password
   ```

2. **Navigate to Dashboard**
   ```
   URL: http://localhost:8000/technician/dashboard/
   ```

---

## Dashboard Layout Overview

### Top Section: Welcome & Statistics
```
┌─────────────────────────────────────────────────────────────┐
│ 👨‍🔧 Technician Dashboard                                   │
│ Welcome back, [Your Name]! Here's your repair workload.     │
├─────────────────────────────────────────────────────────────┤
│ [Total: 5]    [Pending: 2]    [In Progress: 1]  [Done: 2]  │
└─────────────────────────────────────────────────────────────┘
```

**What these mean:**
- **Total**: All repairs assigned to you
- **Pending**: Ready to start (yellow)
- **In Progress**: Currently working on (blue)
- **Completed**: Finished (green)

---

### Main Sections

#### 1. Pending Repairs (Left Column)
```
⚠️ Pending Repairs (2)
├─ Samsung Galaxy S21
│  ├ Customer: John Smith
│  ├ Code: A1B2C3D4E5
│  └ [Click to view details]
└─ iPhone 12
   ├ Customer: Jane Doe
   ├ Code: F6G7H8I9J0
   └ [Click to view details]
```

**Action**: Click a repair card to view details and start working on it.

---

#### 2. In Progress (Right Column)
```
⏳ In Progress (1)
├─ MacBook Pro
│  ├ Customer: Bob Johnson
│  ├ Code: K1L2M3N4O5
│  └ [Click to update]
```

**Action**: Click to add repair logs and update the repair.

---

#### 3. Recently Completed (Full Width)
```
✅ Recently Completed (Last 5)
┌────────────────────────────────────────────────────────┐
│ Gadget      │ Customer    │ Code      │ Completed    │
├─────────────┼─────────────┼───────────┼──────────────┤
│ iPad Mini   │ Alice Brown │ P1Q2R3S4T5│ Feb 20, 2026 │
│ Dell XPS    │ Charlie Lee │ U5V6W7X8Y9│ Feb 19, 2026 │
└────────────────────────────────────────────────────────┘
```

**Action**: Click "View" to see receipt and payment details.

---

#### 4. All Assigned Repairs Table
```
📋 All Assigned Repairs
┌──────────────┬──────────────┬──────────┬──────────┬─────────┐
│ Gadget       │ Customer     │ Status   │ Code     │ Action  │
├──────────────┼──────────────┼──────────┼──────────┼─────────┤
│ Samsung S21  │ John Smith   │ Pending  │ A1B2C3D4E5│ View/Log│
│ iPhone 12    │ Jane Doe     │ Pending  │ F6G7H8I9J0│ View/Log│
│ MacBook Pro  │ Bob Johnson  │ Progress │ K1L2M3N4O5│ View/Log│
└──────────────┴──────────────┴──────────┴──────────┴─────────┘
```

**Actions:**
- **View**: See full repair details and repair logs
- **Add Log**: Record work done on this repair

---

## Common Tasks

### Task 1: Start Working on a Pending Repair

1. **Find the repair** in the "Pending Repairs" section
2. **Click on it** to view details
3. **Update status** from "Pending" → "In Progress"
4. **Add first repair log** (click "Add Repair Log" button)

---

### Task 2: Add a Repair Log (Document Your Work)

**What's a repair log?**
- Record of work done on a repair
- Includes: issue found, solution applied, labor cost

**Steps:**
1. Click **"View Details"** on a repair
2. Click **"Add Repair Log"** button
3. Fill in the form:
   ```
   Issue Description: "Screen was cracked and non-responsive"
   Resolution Description: "Replaced screen with genuine part. Tested OK."
   Repair Cost: 3500 (your charge for this work)
   ```
4. Click **"Save"**

---

### Task 3: Mark Repair as Completed

1. **Add final repair log** with all work details
2. **Update status** to "Completed"
3. **Save changes**

**After this:**
- Secretary can create a receipt
- Customer can pay and collect device

---

### Task 4: View All Your Repairs

1. **Bottom of dashboard**: "All Assigned Repairs" table
2. **Or use**: [My Repairs List](http://localhost:8000/repairs/my-repairs/)
3. Click any repair to see full details

---

## Repair Detail Page Walkthrough

When you click on a repair, you'll see:

```
┌─────────────────────────────────────────────┐
│ REPAIR TRANSACTION: A1B2C3D4E5             │
├─────────────────────────────────────────────┤
│ Device:    Samsung Galaxy S21               │
│ Customer:  John Smith (555-1234)            │
│ Status:    Pending → [Change to In Progress]│
│ Date In:   Feb 21, 2026 10:30 AM            │
├─────────────────────────────────────────────┤
│ REPAIR LOGS (Records of work)               │
├─────────────────────────────────────────────┤
│ Log 1: Screen replacement - $3500           │
│ Log 2: Battery check - $500                 │
│ TOTAL COST: $4000                           │
├─────────────────────────────────────────────┤
│ [Add Repair Log] [Edit] [Mark Complete]     │
└─────────────────────────────────────────────┘
```

---

## Important Tips

### ✅ DO:
- ✅ Update status regularly (so staff knows progress)
- ✅ Add repair logs for each work session
- ✅ Include accurate costs in repair logs
- ✅ Mark complete when you finish
- ✅ Check dashboard daily for new repairs

### ❌ DON'T:
- ❌ Don't forget to update status to "In Progress"
- ❌ Don't leave repairs as "Pending" after starting
- ❌ Don't forget repair logs (helps with receipts)
- ❌ Don't edit past repair logs without reason
- ❌ Don't mark complete until fully done

---

## Keyboard Shortcuts / Quick Links

| Action | Link |
|--------|------|
| Dashboard | `/technician/dashboard/` |
| My Repairs | `/repairs/my-repairs/` |
| All Gadgets | `/gadgets/` |
| All Customers | `/customers/` |
| Logout | `/logout/` |

---

## Troubleshooting

### "I can't see the Dashboard button"
- Make sure you're logged in as a technician
- Check your user role in admin panel

### "I can't see repairs"
- Repairs haven't been assigned to you yet
- Ask your secretary/staff to assign repairs
- Click "View All" to see if any exist

### "I can't edit status"
- Only staff/secretary can change status
- You can only add repair logs
- Contact your manager

### "The page looks weird"
- Clear browser cache: Ctrl+Shift+Del
- Try different browser
- Check if Bootstrap CSS loaded (internet required)

---

## Getting Help

1. **Ask your manager** - They control permissions
2. **Check documentation** - See `TECHNICIAN_DASHBOARD_GUIDE.md`
3. **Review permissions** - See `PERMISSIONS_GUIDE.md`

---

## Dashboard Features Summary

| Feature | Purpose |
|---------|---------|
| Statistics Cards | Quick overview of workload |
| Pending Section | See repairs you need to start |
| In Progress Section | Track what you're working on |
| Completed Section | See finished repairs |
| All Repairs Table | Comprehensive list with filters |
| View Details | See full repair info + logs |
| Add Log Button | Record work done & costs |
| Customer Info | See who owns the device |
| Transaction Code | Unique ID for tracking |

---

## Video Walkthrough (Text Version)

**Scenario: A new repair is assigned to you**

```
1. You log in → Dashboard shows "Pending: 1"
2. Click on repair card in "Pending Repairs" section
3. You see: Samsung S21 for John Smith
4. Click "Change Status" → "In Progress"
5. Click "Add Repair Log"
6. Describe issue: "Screen has burn-in, battery weak"
7. Describe solution: "Screen replacement, battery replacement"
8. Enter cost: 5000
9. Click "Save"
10. Repair log is added
11. After completing: Change status to "Completed"
12. Secretary creates receipt
13. Customer picks up device and pays
```

---

## Next Steps After Dashboard

**After marking repair as "Completed":**
1. Secretary will create receipt
2. Customer will pay the amount
3. You can view payment confirmation
4. Repair closes out

---

*For detailed information, see `TECHNICIAN_DASHBOARD_GUIDE.md` and `PERMISSIONS_GUIDE.md`*
