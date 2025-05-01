from expanded import *
from formatting import *

if __name__ == '__main__': 
    lexer = BasicLexer() 
    parser = BasicParser() 
    print('                                               ')
    print(f'{terminal_colors.HEADER}    Welcome to Utada Programming Language!')
    print(f'{terminal_colors.HEADER}NOW PLAYING: "Simple and Clean" by Utada Hikaru')
    print(f'{terminal_colors.HEADER}↻             ◁     ||     ▷                ↺')
    print(f'{terminal_colors.HEADER}──────────────────────•────────────────────────')

    print(f"""{terminal_colors.HEADER}                                                  
                                                  
          .;+xxxxx:           .;xXXX$X+.          
       .x&&&&&&&&&&&x: .xX: .x&&&&&&&&&&&&;       
     .x&&&&+. ... ;&$&&&&&&&&&&; .:. .x&&&&&:     
    .$&&; x&&&&&&&&&+xx&&&&$+;&&&&&&&&&$.+&&&;    
    x&$..&&&&x..; ;$X&&:..+$&$&+ +..x&&&&x X&&    
    &&..&&x   .&&$x  $&:$&:&&. x&&&:   x&&:.&&.   
    && +&$    ;&.$&&&&xx&&X;&&&&&.&+    &&x &&.   
    && x&&.   .&&; :..&&&&&&..: ;&&:   .&&+ &&.   
    &&& &&&    .&&&&&&&x. x&&&&&&&;    &&& X&&    
    :&&$.&&&;     .::.       :;.     :&&&.X&&+    
     +&&& &&&&.                     $&&& &&&+     
      :&&&&.&&&&.                .&&&&.$&&&:      
        x&&&&:&&&&.            .&&&&+X&&&X        
          X&&&& &&&&.        .&&&&.&&&&x          
            x&&&& &&&&      $&&& &&&&x            
              :&&&& &&&:  :&&&.&&&&:              
                :&&&&&&&;;&&&$&&&:                
                  ;&&&+&&&&x&&&;                  
                    &&&+&&X&&&                    
                     &&&.:&&&                     
                      &&&$&&.                     
                      +&&&&x                      
                      .&&&&.                      
                       x&&x                       
                        ..                        
                                                  
                                                  """) 
    env = {} 
      
    while True:        
        try: 
            text = input(' > ') 
        except EOFError: 
            break
          
        if text: 
            tree = parser.parse(lexer.tokenize(text)) 
            BasicExecute(tree, env)