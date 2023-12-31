function update_schedule() {
  $.ajax({
    url: '/get_approval',
    method: 'get',
    dataType: 'json',
    data: {},
    success: function(data) {
      let schedule_body = document.getElementById('schedule-body');
      while (schedule_body.lastElementChild) {
        schedule_body.removeChild(schedule_body.lastElementChild);
      }

      for (let i = 0; i < Object.keys(data).length; i++) {
        busy = data[Object.keys(data)[i]];
        busy_row = document.createElement('tr');
        cell_day = document.createElement('td');
        cell_from = document.createElement('td');
        cell_to = document.createElement('td');
        cell_company_name = document.createElement('td');
        cell_simulator_name = document.createElement('td');
        cell_action = document.createElement('td');
        cell_day.textContent = busy.day;
        cell_from.textContent = busy.start_time;
        cell_to.textContent = busy.end_time;
        cell_company_name.textContent = busy.company_name;
        cell_simulator_name.textContent = busy.simulator_name;

        busy_row.appendChild(cell_day);
        busy_row.appendChild(cell_from);
        busy_row.appendChild(cell_to);
        busy_row.appendChild(cell_company_name);
        busy_row.appendChild(cell_simulator_name);

        action_approve = document.createElement('button');
        action_decline = document.createElement('button');

        action_approve.textContent = '+';
        action_approve.busy_id = busy.id;
        action_approve.onclick = function(block) {
          $.ajax({
            url: '/send_approve',
            method: 'get',
            dataType: 'json',
            data: {'id': block.srcElement.busy_id, 'approved': 1},
            success: function(data) {
              update_schedule();
            }
          });
        }

        action_decline.textContent = '-';
        action_decline.busy_id = busy.id;
        action_decline.onclick = function(block) {
          $.ajax({
            url: '/send_approve',
            method: 'get',
            dataType: 'json',
            data: {'id': block.srcElement.busy_id, 'approved': 0},
            success: function(data) {
              update_schedule();
            }
          });
        }

        cell_action.appendChild(action_approve);
        cell_action.appendChild(action_decline);

        busy_row.appendChild(cell_action);

        schedule_body.appendChild(busy_row);
      }
    }
  });
}

update_schedule();
