import streamlit as st
import random
import pandas as pd
from datetime import datetime
import re

# Page configuration
st.set_page_config(page_title="Instagram Collaboration Random Draw", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .participant-row {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: white;
        border-left: 4px solid #2b6cb0;
    }
    .participant-row:hover {
        background-color: #f7fafc;
    }
    .moderator-row {
        background-color: #fff5f5;
        border-left: 4px solid #e53e3e;
        text-decoration: line-through;
        color: #666;
    }
    .participant-name {
        flex: 2;
        font-weight: 500;
    }
    .participant-stats {
        flex: 3;
        display: flex;
        gap: 12px;
        color: #666;
    }
    .stat {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .win-chance {
        color: #38a169;
        font-weight: 500;
    }
    .excluded {
        color: #e53e3e;
        font-weight: 500;
    }
    .delete-btn {
        visibility: hidden;
        color: #e53e3e;
        cursor: pointer;
    }
    .participant-row:hover .delete-btn {
        visibility: visible;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎲 Instagram Collaboration Random Draw")
st.markdown("### Monthly selection for an Instagram collaboration with Aurélien or Anthony")

# List of moderators (participants to mark)
MODERATORS = [
    "Tsukoon Art",
    "Melanie Materne",
    "Ai art Insanity",
    "Vikas Chauhan",
    "Julien Durand",
    "Alessandro Manfredi",
    "Altar Erbas",
    "Nick Frei"
]

# Display weighting system
st.markdown("### 🎟️ Weighting System")
st.markdown("""
- **🥇 Top 1:** 4 entries (25% win chance)
- **🥈 Top 2:** 3 entries (18.75% win chance)
- **🥉 Top 3:** 2 entries (12.5% win chance)
- **🏅 Top 4-10:** 1 entry each (6.25% win chance)
""")

# Warning about moderators
st.warning("⚠️ Moderators are excluded from the draw and cannot win.", icon="⚠️")

# Session state initialization
if 'participants' not in st.session_state:
    st.session_state['participants'] = []
if 'draws' not in st.session_state:
    st.session_state['draws'] = []

def parse_leaderboard(text):
    # Split the text into lines and remove empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    participants = []
    current_rank = None
    current_name = None
    current_points = None
    
    for line in lines:
        # Skip the header line
        if line == "Leaderboard (30-day)":
            continue
            
        # If line is a number between 1 and 10, it's a rank
        if line.isdigit() and 1 <= int(line) <= 10:
            current_rank = int(line)
        # If line starts with +, it's a score
        elif line.startswith('+'):
            current_points = int(line.replace('+', ''))
            if current_rank and current_name:
                participants.append((current_name, current_rank, current_points))
            current_name = None
        # Otherwise, it's a name
        else:
            current_name = line
            
    # Add the last participant if needed
    if current_rank and current_name and current_points is not None:
        participants.append((current_name, current_rank, current_points))
        
    return participants

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✏️ Add Participants")
    
    # Add option to paste leaderboard
    st.markdown("#### Option 1: Paste Leaderboard")
    leaderboard_text = st.text_area(
        "Paste your leaderboard here",
        height=300,
        help="Paste the entire leaderboard including ranks, names, and scores"
    )
    
    if st.button("Import from Leaderboard"):
        if leaderboard_text:
            participants = parse_leaderboard(leaderboard_text)
            if len(participants) > 0:
                st.session_state['participants'] = participants
                st.success(f"Successfully imported {len(participants)} participants!")
                st.rerun()
            else:
                st.error("No valid participants found in the text. Please check the format.")
    
    st.markdown("#### Option 2: Add Individual Participant")
    # Add participant form
    with st.form("add_participant"):
        name = st.text_input("Participant name")
        rank = st.number_input("Ranking position", min_value=1, max_value=10, value=1)
        points = st.number_input("Points", min_value=0, value=0)
        submitted = st.form_submit_button("Add")
        
        if submitted and name:
            if name in MODERATORS:
                st.error("Moderators cannot be added to the draw!")
            else:
                # Check if rank is already taken
                existing_ranks = [p[1] for p in st.session_state['participants']]
                if rank in existing_ranks:
                    st.error(f"Position {rank} is already taken!")
                elif len(st.session_state['participants']) >= 10:
                    st.error("Maximum 10 participants allowed!")
                else:
                    st.session_state['participants'].append((name, rank, points))
                    st.success(f"{name} has been added at position {rank}")

with col2:
    st.markdown("### 📋 Participants List")
    if st.session_state['participants']:
        # Create weighted list for win chance calculation
        entry_counts = {
            1: 4,  # Top 1 -> 4 entries
            2: 3,  # Top 2 -> 3 entries
            3: 2,  # Top 3 -> 2 entries
            4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1  # Top 4-10 -> 1 entry each
        }
        
        # Calculate total entries (excluding moderators)
        total_entries = sum(entry_counts[p[1]] for p in st.session_state['participants'] if p[0] not in MODERATORS)
        
        # Container for all participants
        with st.container():
            # Create and display participant rows
            for name, rank, points in sorted(st.session_state['participants'], key=lambda x: x[1]):
                is_moderator = name in MODERATORS
                entries = entry_counts[rank] if not is_moderator else 0
                win_chance = (entries / total_entries * 100) if (not is_moderator and total_entries > 0) else 0
                
                # Create row with delete button
                col_info, col_btn = st.columns([20, 1])
                
                with col_info:
                    row_class = "participant-row moderator-row" if is_moderator else "participant-row"
                    st.markdown(f"""
                    <div class="{row_class}">
                        <div class="participant-name">
                            {name} {' ❌' if is_moderator else ''}
                        </div>
                        <div class="participant-stats">
                            <span class="stat">#{rank}</span>
                            <span class="stat">🏆 {points}pts</span>
                            <span class="stat">🎟️ {entries}</span>
                            <span class="{'excluded' if is_moderator else 'win-chance'}">
                                {f"EXCLUDED" if is_moderator else f"{win_chance:.1f}%"}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    if st.button("🗑️", key=f"delete_{name}", help=f"Delete {name}"):
                        st.session_state['participants'] = [p for p in st.session_state['participants'] if p[0] != name]
                        st.rerun()
            
            if st.button("🗑️ Clear All"):
                st.session_state['participants'] = []
                st.rerun()

# Random draw section
st.markdown("---")
st.markdown("### 🎯 Random Draw")

if st.session_state['participants']:
    # Create weighted list (excluding moderators)
    entries = []
    for name, rank, _ in st.session_state['participants']:
        if name not in MODERATORS:  # Only add non-moderators to the draw
            entries.extend([name] * entry_counts[rank])
    
    # Display total entries
    st.info(f"Total number of entries in the draw: {len(entries)}")
    
    # Button to perform the draw
    if st.button("🎲 Draw Winner"):
        if entries:  # Only perform draw if there are valid entries
            winner = random.choice(entries)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Find winner's points
            winner_points = next(points for name, _, points in st.session_state['participants'] if name == winner)
            st.session_state['draws'].append({
                "Date": timestamp,
                "Winner": winner,
                "Points": winner_points,
                "Status": "Participant"  # Always participant since moderators are excluded
            })
            st.balloons()
            st.success(f"🎉 The winner is: **{winner}** (Points: {winner_points})")
        else:
            st.error("No eligible participants for the draw!")
else:
    st.warning("Please add participants before performing a draw.")

# Display draw history
if st.session_state['draws']:
    st.markdown("---")
    st.markdown("### 📜 Draw History")
    df_history = pd.DataFrame(st.session_state['draws'])
    st.dataframe(df_history, hide_index=True)
    
    # Button to download history
    csv = df_history.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download History (CSV)",
        data=csv,
        file_name=f'draw_history_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
    
    # Button to clear history
    if st.button("🗑️ Clear History"):
        st.session_state['draws'] = []
        st.rerun()