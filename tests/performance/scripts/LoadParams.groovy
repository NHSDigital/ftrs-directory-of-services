import java.nio.file.Files
import java.nio.file.Paths

def csvPath = "parameter_files/test_params.csv"
def file = new File(csvPath)

if (file.exists()) {

    def lines = file.readLines()

    // For each line, split by comma and set variables
    lines.eachWithIndex { line, idx ->
        def values = line.split(",")

        // Set each value as a variable, e.g. param_0_0, param_0_1, ...
        values.eachWithIndex { val, col ->
            props.put("param_${idx}_${col}", val)
        }
    }
}

// Set Apim_Env
def Apim_Env = props.get("apim_env")
if (Apim_Env == null || Apim_Env == "") {
    Apim_Env = vars.get("param_0_0")
}
if (Apim_Env != null) {
    props.put("Apim_Env", Apim_Env)
}

// Set Environment
def Env = props.get("env")
if (Env == null || Env == "") {
    Env = vars.get("param_0_1")
}
if (Env != null) {
    props.put("Env", Env)
}

// Set AWS Secret
def AWS_SECRET_NAME = props.get("AWS_SECRET_NAME")
if (AWS_SECRET_NAME == null || AWS_SECRET_NAME == "") {
    AWS_SECRET_NAME = vars.get("param_0_2")
}
if (AWS_SECRET_NAME != null) {
    props.put("AWS_SECRET_NAME", AWS_SECRET_NAME)
}

// Set ServiceEndpoint
def serviceendpoint = props.get("serviceendpoint")
if (serviceendpoint == null || serviceendpoint == "") {
    serviceendpoint = vars.get("param_0_3")
}
if (serviceendpoint != null) {
    props.put("ServiceEndpoint", serviceendpoint)
}

def workspace = props.get("workspace")
if (workspace == null || workspace == "") {
    workspace = vars.get("param_0_4")
}
if (workspace == "default") {
    props.put("Workspace", "")
} else if (workspace != null && workspace != "") {
    props.put("Workspace", "-" + workspace)
}


props.put("Apim_Workspace", "dos-search" + (props.get("Workspace") ?: ""))

// Calculate exact_limit (Total Executions) for PreciseThroughputTimer
// = (throughput / throughputPeriod) * duration
def timerThroughput = (props.get("timer_throughput") ?: "9000").toDouble()
def timerPeriod = (props.get("timer_throughput_period") ?: "60").toDouble()
def testDuration = (props.get("duration") ?: "3660").toDouble()
def exactLimit = ((timerThroughput / timerPeriod) * testDuration) as int
props.put("exact_limit", exactLimit.toString())
log.info("Calculated exact_limit=${exactLimit} (throughput=${timerThroughput}/period=${timerPeriod} * duration=${testDuration})")


log.info("Loaded APIM Params: Apim_Env=${props.get("Apim_Env")},Apim_Workspace=${props.get("Apim_workspace")},  Env=${props.get("Env")}, AWS_SECRET_NAME=${props.get("AWS_SECRET_NAME")}")
log.info("Loaded Backend Params: ServiceEndpoint=${props.get("ServiceEndpoint")}, Workspace=${props.get("Workspace")}")
