login_select = document.getElementById('login');

$.ajax({
  url: '/get_logins',
  method: 'get',
  dataType: 'json',
  data: {},
  success: function(data) {
    console.log(data);
    for (let i = 0; i < Object.keys(data).length; i++) {
      user = data[Object.keys(data)[i]];
      option_tag = document.createElement('option');
      option_tag.setAttribute('value', user.id);
      option_tag.textContent = user.name;
      login_select.appendChild(option_tag);
    }
  }
});