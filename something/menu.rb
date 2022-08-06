require "tty-prompt"
require "tty-progressbar"
require "pastel"

prompt = TTY::Prompt.new(active_color: :cyan)
pastel = Pastel.new(enabled: true)
continue = true

puts pastel.white("=== Hello. Welcome to ") + pastel.decorate("TTY ON CLOUD", :cyan, :bold) + pastel.white(" ===")
while continue
    choices = ["Upload files", "Start Fuzzing"]

    selection =  prompt.select("\nCheck out: ", choices) 
    
    if selection == choices[0]
        puts "#TODO" 
    elsif selection == choices[1]
        #puts "Type " + pastel.decorate("exit ", :cyan, :bold) + "to quit"
        puts "Select a file to fuzz: "
    end
end
