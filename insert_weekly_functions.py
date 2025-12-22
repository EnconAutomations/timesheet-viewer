#!/usr/bin/env python3
"""
Script to insert weekly view JavaScript functions into ViewerV4.html
"""

# Read the current file
with open('/Users/mniji/Downloads/TimesheetV4/ViewerV4.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "// --- CALENDAR LOGIC ---"
insert_position = None
for i, line in enumerate(lines):
    if '// --- CALENDAR LOGIC ---' in line:
        insert_position = i
        break

if insert_position is None:
    print("Could not find insertion point")
    exit(1)

# Weekly functions to insert
weekly_functions = '''
        // --- WEEKLY VIEW LOGIC ---
        
        function changeWeek(offset) {
            if (!currentWeekStart) return;
            currentWeekStart.setDate(currentWeekStart.getDate() + (offset * 7));
            renderWeekView();
        }

        function goToCurrentWeek() {
            const today = new Date();
            const dayOfWeek = today.getDay();
            const diff = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek;
            currentWeekStart = new Date(today);
            currentWeekStart.setDate(today.getDate() + diff);
            renderWeekView();
        }

        function formatDateYMD(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        function aggregateWeekData() {
            if (!currentWeekStart || !appData || !appData.discrepancies) {
                return { weekData: {}, weekDates: [], techNames: [] };
            }

            const weekData = {};
            const weekDates = [];

            for (let i = 0; i < 7; i++) {
                const date = new Date(currentWeekStart);
                date.setDate(currentWeekStart.getDate() + i);
                weekDates.push(formatDateYMD(date));
            }

            appData.discrepancies.forEach(item => {
                if (!weekDates.includes(item.date)) return;

                if (!weekData[item.employeeName]) {
                    weekData[item.employeeName] = {};
                    weekDates.forEach(d => {
                        weekData[item.employeeName][d] = { HIGH: 0, MEDIUM: 0 };
                    });
                }

                const severity = item.severity === 'HIGH' ? 'HIGH' : 'MEDIUM';
                weekData[item.employeeName][item.date][severity]++;
            });

            const techNames = Object.keys(weekData).sort();

            return { weekData, weekDates, techNames };
        }

        function renderWeekView() {
            if (!currentWeekStart) return;

            const { weekData, weekDates, techNames: allTechNames } = aggregateWeekData();

            // Filter to show only techs with HIGH severity items this week
            const techNames = allTechNames.filter(tech => {
                let hasHigh = false;
                weekDates.forEach(d => {
                    if (weekData[tech][d].HIGH > 0) hasHigh = true;
                });
                return hasHigh;
            });

            const startDate = new Date(currentWeekStart);
            const endDate = new Date(currentWeekStart);
            endDate.setDate(startDate.getDate() + 6);
            const titleStr = `Week of ${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
            document.getElementById('week-title').innerText = titleStr;

            let weekHighTotal = 0;
            let weekMedTotal = 0;
            techNames.forEach(tech => {
                weekDates.forEach(date => {
                    weekHighTotal += weekData[tech][date].HIGH;
                    weekMedTotal += weekData[tech][date].MEDIUM;
                });
            });
            document.getElementById('week-high-total').innerText = weekHighTotal;
            document.getElementById('week-med-total').innerText = weekMedTotal;

            const gridContainer = document.getElementById('weekly-grid');
            gridContainer.innerHTML = '';

            if (techNames.length === 0) {
                gridContainer.innerHTML = `
                    <div class="text-center py-12 text-slate-500">
                        <i class="fa-solid fa-calendar-xmark text-4xl mb-4 opacity-50"></i>
                        <p class="text-lg">No discrepancies for this week</p>
                    </div>
                `;
                renderTechSummaryTable({}, []);
                return;
            }

            let gridHTML = '<div class="overflow-x-auto">';
            gridHTML += '<table class="w-full border-collapse">';

            gridHTML += '<thead><tr class="border-b border-white/10">';
            gridHTML += '<th class="text-left py-3 px-4 text-slate-400 text-xs font-medium uppercase tracking-wider sticky left-0 bg-slate-800/50 backdrop-blur z-10">Technician</th>';
            const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            weekDates.forEach((dateStr, idx) => {
                const date = new Date(dateStr);
                const dayName = dayNames[idx];
                const monthDay = date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' });
                gridHTML += `<th class="text-center py-3 px-4 min-w-[80px]">
                    <div class="text-slate-400 text-xs font-medium uppercase tracking-wider">${dayName}</div>
                    <div class="text-slate-500 text-[10px] mt-0.5">${monthDay}</div>
                </th>`;
            });
            gridHTML += '</tr></thead>';

            gridHTML += '<tbody>';
            techNames.forEach(techName => {
                gridHTML += '<tr class="border-b border-white/5 hover:bg-white/[0.02] transition">';
                gridHTML += `<td class="py-3 px-4 font-medium text-slate-200 sticky left-0 bg-slate-800/70 backdrop-blur z-10">${techName}</td>`;

                weekDates.forEach(dateStr => {
                    const high = weekData[techName][dateStr].HIGH;
                    const med = weekData[techName][dateStr].MEDIUM;
                    const total = high + med;

                    let bgClass, textClass, borderClass;
                    if (high === 0) {
                        bgClass = 'bg-slate-800/20';
                        textClass = 'text-slate-600';
                        borderClass = 'border-slate-700/30';
                    } else {
                        bgClass = 'bg-red-500/20 hover:bg-red-500/30';
                        textClass = 'text-red-400';
                        borderClass = 'border-red-500/30';
                    }

                    const clickable = total > 0 ? 'cursor-pointer' : '';
                    const onclick = total > 0 ? `onclick="openWeekCell('${techName}', '${dateStr}')"` : '';

                    gridHTML += `<td class="text-center py-3 px-4">
                        <div class="${bgClass} ${clickable} py-2 px-3 rounded-lg border ${borderClass} transition-all" ${onclick}>
                            <div class="${textClass} text-lg font-bold font-mono">${high}</div>
                            ${med > 0 ? `<div class="text-slate-500 text-[10px] mt-0.5">+${med} med</div>` : ''}
                        </div>
                    </td>`;
                });

                gridHTML += '</tr>';
            });
            gridHTML += '</tbody></table></div>';

            gridContainer.innerHTML = gridHTML;

            renderTechSummaryTable(weekData, techNames);
        }

        function renderTechSummaryTable(weekData, techNames) {
            const tbody = document.getElementById('tech-summary-body');
            tbody.innerHTML = '';

            if (techNames.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-slate-500">No data for this week</td></tr>';
                return;
            }

            const techTotals = techNames.map(techName => {
                let high = 0, med = 0;
                Object.values(weekData[techName]).forEach(counts => {
                    high += counts.HIGH;
                    med += counts.MEDIUM;
                });
                return { name: techName, high, med, total: high + med };
            }).filter(t => t.high > 0);

            techTotals.sort((a, b) => b.high - a.high || a.name.localeCompare(b.name));

            techTotals.forEach(tech => {
                const row = document.createElement('tr');
                row.className = 'border-b border-white/5 hover:bg-white/[0.02] transition cursor-pointer';
                row.onclick = () => openTechSummary(tech.name);

                row.innerHTML = `
                    <td class="py-3 px-4 text-slate-200 font-medium">${tech.name}</td>
                    <td class="py-3 px-4 text-center">
                        <span class="inline-block px-2 py-1 rounded ${tech.high > 0 ? 'bg-red-500/10 text-red-400' : 'text-slate-600'} font-mono font-bold">
                            ${tech.high}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-center">
                        <span class="inline-block px-2 py-1 rounded ${tech.med > 0 ? 'bg-amber-500/10 text-amber-400' : 'text-slate-600'} font-mono">
                            ${tech.med}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-center text-slate-300 font-mono font-bold">${tech.total}</td>
                `;

                tbody.appendChild(row);
            });
        }

        function openWeekCell(techName, dateStr) {
            currentFilter.search = techName;
            currentFilter.severity = 'ALL';
            document.getElementById('search-input').value = techName;
            document.getElementById('severity-filter').value = 'ALL';
            renderSidebar();
            switchView('list');

            const firstHigh = appData.discrepancies.find(i => 
                i.employeeName === techName && i.date === dateStr && i.severity === 'HIGH'
            );
            const firstAny = appData.discrepancies.find(i => 
                i.employeeName === techName && i.date === dateStr
            );
            const item = firstHigh || firstAny;
            if (item) loadDetail(item);
        }

        function openTechSummary(techName) {
            currentFilter.search = techName;
            currentFilter.severity = 'ALL';
            currentFilter.flag = 'ALL';
            document.getElementById('search-input').value = techName;
            document.getElementById('severity-filter').value = 'ALL';
            document.getElementById('flag-filter').value = 'ALL';
            renderSidebar();
            switchView('list');

            const firstItem = appData.discrepancies.find(i => i.employeeName === techName);
            if (firstItem) loadDetail(firstItem);
        }


'''

# Insert the weekly functions before the calendar logic line
lines.insert(insert_position, weekly_functions)

# Write back to file
with open('/Users/mniji/Downloads/TimesheetV4/ViewerV4.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully inserted weekly view functions")
