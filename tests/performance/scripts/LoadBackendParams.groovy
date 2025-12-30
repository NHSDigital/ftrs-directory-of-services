import java.nio.file.Files
import java.nio.file.Paths

def csvPath = "parameter_files/backend_params.csv"
def file = new File(csvPath)

if (file.exists()) {

    def lines = file.readLines()

    // For each line, split by comma and set variables
    lines.eachWithIndex { line, idx ->
        def values = line.split(",")
        log.info("here1")

        // Set each value as a variable, e.g. param_0_0, param_0_1, ...
        values.eachWithIndex { val, col ->
            vars.put("param_${idx}_${col}", val)
        }
    }
}

// Set ServiceEndpoint
def pp_endpoint = vars.get("param_0_0")

def serviceendpoint = props.get("serviceendpoint")
if (serviceendpoint == null || serviceendpoint == "") {
    serviceendpoint = pp_endpoint
}
vars.put("ServiceEndpoint", serviceendpoint)
