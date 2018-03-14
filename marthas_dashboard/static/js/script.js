// JS for Energy Comps

//----Main compare graph & alerts----
//-----------------------------------
// Change drowndowns responsively (when building changes, point options change)
$('#ptCompare-buildingSel-0').change(function () {updatePointSel(0)})
$('#ptCompare-buildingSel-1').change(function () {updatePointSel(1)})

function updatePointSel (i) {
  let building_id = $('#ptCompare-buildingSel-' + i).val()
  let ptChoice = $('#ptCompare-ptSel-' + i)
  let ptValues = selectorData[building_id]['points']
  ptChoice.empty()
  $.each(ptValues, function (idx, value) {
    let option_text = `<option value=${idx}>${value['name']} - ${value['description']}</option>`
    // console.log(option_text)
    ptChoice.append(option_text)
  })
}

// Loads ptCompare plot when form submitted
$('.ptCompare-form').on('submit', function (event) {
  event.preventDefault()

  let plotId = '#plot-' + this.dataset.idx
  let scriptId = '#script-' + this.dataset.idx
  let tool = this.dataset.tool

  let base_url = $SCRIPT_ROOT + '/_make_compare_plot/?'
  let args = $(this).serialize() + '&tool=' + tool
  let url = base_url + args

  $.getJSON(url, {}, function (data) {
    console.log(data)
    $(plotId).html(data.plot)
    $(scriptId).html(data.script)
    if (tool === 'alerts') {
      updateAlertsTable(data.table)
    }
  })
  return false
})

// Construct alerts table (in fun, function chaining style!)
function updateAlertsTable (table_json) {
  let table = $('<table>').addClass('table table-hover').append([
    $('<thead>').append(
      $('<tr>').append(
        $.map(['Time', 'Value', 'Units'], function (value) {
          return $('<th>').text(value)
        }))),
    $('<tbody>').append(
      $.map(table_json, function (value) {
        return $('<tr>').append(
          $('<td>').text(value.pointtimestamp),
          $('<td>').text(value.pointvalue),
          $('<td>').text(value.units))
      }))])
  $('#alerts-table').html(table)
}

//-----------Room Compare------------
//-----------------------------------
// Loads roomCompare table when form submitted
$('.rmCompare-form').on('submit', function (event) {
  event.preventDefault()

  let base_url = $SCRIPT_ROOT + '/_make_room_compare_table/?'
  let args = $(this).serialize()
  let url = base_url + args

  $.getJSON(url, function (table) {
    console.log(table)
    if (table) {
      updateRoomCompareTable(table)
    }
    else { $('#compare-table').html('Sorry, no data! Maybe try Evans...') }
  })
  return false
})

// Construct room compare table (in fun, function chaining style!)
function updateRoomCompareTable (table_json) {
  let table = $('<table>').addClass('table table-hover sortable room-compare-table').append([
    $('<thead>').append(
      $('<tr>').append(
        $.map(['Room', 'Valve %', 'Room Temp'], function (value) {
          return $('<th>').text(value)
        }))),
    $('<tbody>').append(
      $.map(table_json, function (row) {
        return $('<tr>').append(
          $('<td headers="room">').text(row.name_room),
          $('<td headers="valve">').text(row.valve).addClass(row.valve_anomalous ? 'bg-warning' : ''),
          $('<td headers="room_temp">').text(row.room_temp).addClass(row.room_temp_anomalous ? 'bg-warning' : ''))
      }))])

  $('#compare-table').html(table)
}

// Load room inspector page when room compare table cell clicked
$('#compare-table').on('click', '.room-compare-table > tbody > tr', function () {
  let data = []
  $(this.children).each(function (colIndex, col) {
    data.push(col.headers + '=' + col.textContent)
  })

  let roomText = data[0].replace('=', ' ')
  data.push('date=' + document.getElementById('date_select').value)
  data.push('timestamp=' + document.getElementById('timestamp_select').value)
  data.push('building=' + document.getElementById('building_select').value)
  let url = $SCRIPT_ROOT + '/_make_room_compare_plots/?' + data.join('&')

  $.getJSON(url, {}, function (data) {
    $('#rmComparePlotsTitle').html($('<h3>').text(`${roomText}`))
    $('#rmComparePlots').html(data.plot)
    $('#rmCompareScript').html(data.script)
  })
  return false
})



