// Список месяцев
const months = [
    "Январь", "Февраль", "Март",
    "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь",
    "Октябрь", "Ноябрь", "Декабрь"
  ];

// Получаем текущую дату
const currentDate = new Date();

// Переменные для расписания
var checked_count = 0;
var selected_day = '';

// Функция для получения дней в месяце
function getDaysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

// Функция для создания ячеек календаря
function createCalendarCells(year, month) {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const totalDays = getDaysInMonth(year, month);
  
  let startDay = firstDay.getDay(); // День недели, с которого начинается месяц
  if (startDay == 0) startDay = 7;
  startDay--;

  const calendarBody = document.getElementById("calendar-body");
  calendarBody.innerHTML = ""; // Очищаем предыдущий месяц

  $.ajax({
    url: '/month/',
    method: 'get',
    dataType: 'json',
    data: {'month': month + 1, 'year': year, 'simulator_id': simulator_id},
    success: function(data) {
      let dayCount = 1;

      for (let i = 0; i < 6; i++) {
        const row = document.createElement("tr");

        for (let j = 0; j < 7; j++) {
          const cell = document.createElement("td");

          if ((i === 0 && j < startDay) || dayCount > totalDays) {
            // Пустые ячейки до начала месяца и после его окончания
            cell.textContent = "";
          } else {
            cell.date = dayCount + "." + (month + 1) + "." + year;

            cell.onclick = function() {
              let date_block = event.srcElement;

              selected_day = date_block.date;

              last_selected_day = document.getElementById('selected_day');
              if (last_selected_day) {
                last_selected_day.removeAttribute('id');
              }
              date_block.setAttribute('id', 'selected_day');

              document.getElementById("schedule-block").removeAttribute('hidden');
              document.getElementById("schedule-date").innerHTML = date_block.date;

              $.ajax({
                url: '/day/',
                method: 'get',
                dataType: 'json',
                data: {'day': date_block.date, 'simulator_id': simulator_id},
                success: function(data) {

                  let schedule_body = document.getElementById("schedule-body");
                  while (schedule_body.lastElementChild) {
                    schedule_body.removeChild(schedule_body.lastElementChild);
                  }

                  for (let i = 0; i < Object.keys(data).length; i++) {
                    let busy = data[Object.keys(data)[i]];
                    busy_row = document.createElement("tr");
                    cell_n = document.createElement("td");
                    cell_from = document.createElement("td");
                    cell_to = document.createElement("td");
                    cell_name = document.createElement("td");
                    cell_n.textContent = i + 1;
                    cell_from.textContent = busy.start_time;
                    cell_to.textContent = busy.end_time;
                    cell_name.textContent = busy.company_name;

                    if (busy.approved == 0) {
                      cell_name.textContent += ' (на рассмотрении)';
                    }

                    busy_row.appendChild(cell_n);
                    busy_row.appendChild(cell_from);
                    busy_row.appendChild(cell_to);
                    busy_row.appendChild(cell_name);

                    schedule_body.appendChild(busy_row);
                  }
                }
              });
            };

            cell.textContent = dayCount;
            dayCount++;
          }

          row.appendChild(cell);
        }

        calendarBody.appendChild(row);

        if (dayCount > totalDays) {
          break;
        }
      }
    }
  });
}

// Функция для обновления заголовка с текущим месяцем
function updateCalendarHeader(year, month) {
  const currentMonthElement = document.getElementById("current-month");
  currentMonthElement.textContent = `${months[month]} ${year}`;

  document.getElementById("schedule-block").setAttribute('hidden', 'hidden');
}

// Инициализация календаря
function initCalendar() {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  updateCalendarHeader(year, month);
  createCalendarCells(year, month);
}

function prevMonth() {
  currentDate.setMonth(currentDate.getMonth() - 1);
  updateCalendar();
}

function nextMonth() {
  currentDate.setMonth(currentDate.getMonth() + 1);
  updateCalendar();
}

function updateCalendar() {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  updateCalendarHeader(year, month);
  createCalendarCells(year, month);
}

// Вызываем инициализацию календаря
initCalendar();