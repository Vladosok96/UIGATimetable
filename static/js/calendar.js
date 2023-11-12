// Получаем текущую дату
const currentDate = new Date();

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

  let dayCount = 1;

  for (let i = 0; i < 6; i++) {
    const row = document.createElement("tr");

    for (let j = 0; j < 7; j++) {
      const cell = document.createElement("td");

      if ((i === 0 && j < startDay) || dayCount > totalDays) {
        // Пустые ячейки до начала месяца и после его окончания
        cell.textContent = "";
      } else {
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

// Функция для обновления заголовка с текущим месяцем
function updateCalendarHeader(year, month) {
  const months = [
    "Январь", "Февраль", "Март",
    "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь",
    "Октябрь", "Ноябрь", "Декабрь"
  ];
  const currentMonthElement = document.getElementById("current-month");
  currentMonthElement.textContent = `${months[month]} ${year}`;
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