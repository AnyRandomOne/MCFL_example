package com.sklcs.mainProject;
//import static com.github.javaparser.ParserConfiguration.LanguageLevel.JAVA_7;
//import com.github.javaparser.JavaParser;

public class JavaProjectParser {
    public static void main(String args[]) throws Exception {
        //arg 0: type of resolve; 1: source path; 2: result file
        //System.out.println("start process");
        //JavaParser.get
        AbstractResolver resolver;
        //judge the type of args
        switch (args[0]){
            case "testFile":
                resolver = new TestFileResolver(args[1]);
                break;
            case "allJavaFilesInPath":
            default:
                resolver = new AllFileResolver(args[1], fileSuffix(args[2]));
        }
        //now there are only one type of parsers
        switch(args[2]){
            case "border":
                resolver.setParser(new AddBordersParser(args[3]));
                break;
            case "method":
                resolver.setParser(new MethodCallParser(args[3]));
                break;
            case "variable":
                resolver.setParser(new VariableParser(args[3]));
                break;
            case "split":
                resolver.setParser(new TestCaseSplitParser(args[3]));
                break;
            case "predicate":
                resolver.setParser(new PredicateVariableParser(args[3]));
                break;
            case "key":
                resolver.setParser(new KeyVariableParser(args[3]));
                break;
            default:
                resolver.setParser(new AddBordersParser(args[3]));
        }
        //System.out.println("succeed set parser");
        resolver.resolve();
        resolver.parser.writer.close();

        //System.out.println("end process");
    }

    private static String fileSuffix(String task){
        switch (task){
            case "border":
            case "variable":
            case "split":
            case "predicate":
            case "key":
                return "java";
            case "method":
            default:
                return "class";
        }
    }
}
