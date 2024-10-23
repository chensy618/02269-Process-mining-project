var taskTable;

// Update the task list.
function fillDcrTable(status) {
    for (var row of status)
    {
        row.executed = (row.executed ? "V:" + row.lastExecuted : "");            
        row.pending = (row.pending ? "!" + (row.deadline === undefined ? "" : ":" + row.deadline) : "");            
        row.included = (row.included ? "" : "%");       
        row.name = "<button " + (row.enabled ? "" : "disabled") + " onclick=\"graph1.execute('" + row.name + "');fillDcrTable(graph1.status());\">" + row.label + "</button>";
    }
    taskTable.load(status);
    updateAccepting(graph1.isAccepting());
}

// Show if the graph is accepting or not.
function updateAccepting(status) {
    document.getElementById("accepting").innerHTML = (status ? "Accepting" : "Not accepting");
}

$(document).ready(function(e) {    
    taskTable = dynamicTable.config('task-table', 
    ['executed', 'included', 'pending', 'enabled', 'name'], 
    ['Executed', 'Included', 'Pending', 'Enabled', 'Name'], 
    'There are no items to list...'); 

    // update the input DCR Graph
    $('#ta-dcr').keyup(function(e) {
        var x = document.getElementById("ta-dcr");
        try{
            graph1 = parser.parse(x.value);        
            fillDcrTable(graph1.status());
            document.getElementById("parse-error").innerHTML = "";
        }
        catch(err)
        {
            document.getElementById("parse-error").innerHTML = err.message + "</br>" + JSON.stringify(err.location);
        }
    });         


    // update the log
    $('#ta-log').keyup(function(e) {
        var x = document.getElementById("ta-log");
        try{
            
            // Load the log in CSV format
            var y = document.getElementById("ta-log");
            var rawlog = y.value;
            var log = $.csv.toArrays(rawlog, {
                delimiter: "'", // Sets a custom value delimiter character
                separator: ';', // Sets a custom field separator character
              });
            console.log(JSON.stringify(log));
            
            graph1.log = log;

            document.getElementById("log-details").innerHTML = "Log parsed </br>";

            // go through the log and show some basic statistics
            var count_events = 0;
            var cases = new Set();
            var activities = new Set();
            for (var line of log)
            {
                count_events++;
                var caseid = line[0];
                var activity = line[2];
                cases.add(caseid);
                activities.add(activity);
            }

            document.getElementById("log-details").innerHTML += "Events: " + count_events + " </br>";
            document.getElementById("log-details").innerHTML += "Cases: " + cases.size + " </br>";
            document.getElementById("log-details").innerHTML += "Acitivites: </br>";
            for (var a of activities)
            {
                document.getElementById("log-details").innerHTML += a + "</br>";
            }
        }
        catch(err)
        {
            document.getElementById("parse-error").innerHTML = err.message + "</br>" + JSON.stringify(err.location);
        }
    });         

    
    try{
        var x = document.getElementById("ta-dcr");
        graph1 = parser.parse(x.value);                
        fillDcrTable(graph1.status());
        document.getElementById("parse-error").innerHTML = "";
    }
    catch(err)
    {
        document.getElementById("parse-error").innerHTML = err.message + "</br>" + JSON.stringify(err.location);
    }

});