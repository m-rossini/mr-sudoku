# Instructions on Design and Coding and Testing and Standards
## Design
1. Enforce single principle of responsability
1. Prefer composition over inheritance
1. Make evolution and maiontenance easier by enforcing open for extension closed for modification principle
1. Enforce interface segregation principle
1. Enforce dependency injection principle
1. Optimize for human understanding of the design and code

## Coding
1. whenever you create a logger.debug code, please prefix the string with '>' and also add the class and method name in the form ClassName::MethodName
1. whenever you create a logger.info code, please prefix the string with '>>' and also add the class and method name in the form ClassName::MethodName
1. whenever you create a logger.warn code, please prefix the string with '>>>' and also add the class and method name in the form ClassName::MethodName
1. whenever you create a logger.error code, please prefix the string with '>>>>' and also add the class and method name in the form ClassName::MethodName

## Testing
1. Test interfaces do not test implementation details

## Standards
1. I am using zsh in linux
1. Ensure import statements are always at the top of the file. In python import comes before from
1. Never create a highlevel package named utils,. helper, common or such generic type names




