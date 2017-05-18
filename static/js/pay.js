/**
 * Created by lz on 2015/12/19.
 */
$(document).ready(function() {
        $('#monthSelect').change(function () {
            var type = $('input[name=accoutType]:checked').val()
            var month = $(this).children('option:selected').val()
            $('#money').val(month * type)
            $('#month').val(month)
        })

    $("input[name=accoutType]").click(function(){
        var type = $('input[name=accoutType]:checked').val()
        var month = $('#monthSelect').children('option:selected').val()
        $('#money').val(month * type)
    })
})