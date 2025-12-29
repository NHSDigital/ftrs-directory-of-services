import java.nio.file.Files
import java.nio.file.Paths

def csvPath = "parameter_files/apim_params.csv"
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

def pp_apim_env = vars.get("param_0_0")

def Apim_Env = props.get("apim_env")
if (Apim_Env == null || Apim_Env == "") {
    Apim_Env = pp_apim_env
}
vars.put("Apim_Env", Apim_Env)
