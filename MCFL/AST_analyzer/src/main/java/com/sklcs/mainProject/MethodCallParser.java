package com.sklcs.mainProject;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.*;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.AnnotationDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.Node;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.*;

//import static com.github.javaparser.ParserConfiguration.LanguageLevel.*;

public class MethodCallParser extends AbstractParser {
    private Set<String> packageSet;
    //private Map<String, Set<String>> callgraphDict;
    private Map<String, String> callgraphDict;

    //    format: class -> Set<Method>
    private Map<String, Set<String>> classMethodDict;

    //    format superclass -> Set<subclass>
    private Map<String, Set<String>> inheritDict;
    private int lineNo;
    private String packageNow;
    public MethodCallParser(String resultFile) throws IOException {
        //String[] header = new String[]{"type", "file", "start", "end"};
        //super(resultFile, header);
        super(resultFile, new String[]{"line", "method_call"}, 2);
        this.packageSet = new HashSet<>();
        this.callgraphDict = new HashMap<>();
        this.classMethodDict = new HashMap<>();
        this.inheritDict = new HashMap<>();
        this.lineNo = 0;
    }

    @Override
    public void parse(String filePath) {
        try{
            //System.out.println(filePath);
            this.writer.setFileNow(filePath);
            FileInputStream fileInputStream = new FileInputStream(filePath);
            //StaticJavaParser.getConfiguration().setLanguageLevel(JAVA_1_4);
            //System.out.println(filePath);
            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            cu.accept(new MethodCallVisitor(), this.writer);
        }
        catch (FileNotFoundException e){
            System.out.println("file not found" + e);
        }
    }

    @Override
    public void parse(ArrayList<String> filePathArray){
        for(String fileName: filePathArray){
            collect_package(fileName);
        }
        for(String fileName: filePathArray){
            collect_call(fileName);
        }
    }

    private void collect_package(String fileName){
        try{
            this.writer.setFileNow(fileName);
            FileInputStream fileInputStream = new FileInputStream(fileName);
//            CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            //System.out.println("packageDeclaration: "+ cu.getPackageDeclaration().get().getName().toString());
            //System.out.println("module: " + cu.getModule().get().toString());
//            if(cu.getPackageDeclaration().isPresent()){
//                String packageName = cu.getPackageDeclaration().get().getName().toString();
//                this.packageSet.add(packageName);
//            }
            ClassNode classNode = new ClassNode();
            ClassReader classReader = new ClassReader(fileInputStream);
            classReader.accept(classNode, 0);

            List<String> wordList = Arrays.asList(classNode.name.split("/"));
            String packageName = String.join(".", wordList.subList(0, (wordList.size()-1)));
            this.packageSet.add(packageName);
        } catch(Exception e){
            System.out.println("collect package: "+e);
        }
    }

    private void collect_call(String fileName){
        try{
            //System.out.println("start collect call");
            this.writer.setFileNow(fileName);
            //System.out.println("file: "+ fileName);
            FileInputStream fileInputStream = new FileInputStream(fileName);
            //System.out.println("new fileInputStream");
            //CompilationUnit cu = StaticJavaParser.parse(fileInputStream);
            //System.out.println(cu.toString());
            //cu.accept(new MethodCallVisitor(), this.writer);
            ClassNode classNode = new ClassNode();
            //System.out.println("new classNode");
            ClassReader classReader = new ClassReader(fileInputStream);
            //System.out.println("new classReader");
            classReader.accept(classNode, 0);
            //System.out.println("start to replace");
            String callerClassName = classNode.name.replace('/', '.');
            //System.out.println("callerClassName: " + callerClassName);

            // check if class name is in classMethodDict
            if (!this.classMethodDict.containsKey(callerClassName)){
                this.classMethodDict.put(callerClassName, new HashSet<>());
            }

            // check if class has a superclass
            List<String> superNameWordList = Arrays.asList(classNode.superName.split("/"));
            String superPkgName = String.join(".", superNameWordList.subList(0, (superNameWordList.size()-1)));
            String superClassName = classNode.superName.replace('/', '.');
            if (this.packageSet.contains(superPkgName)){
                if(!this.inheritDict.containsKey(superClassName)){
                    this.inheritDict.put(superClassName, new HashSet<>());
                }
                this.inheritDict.get(superClassName).add(callerClassName);
            }

            List<MethodNode> methodList = classNode.methods;
            for ( MethodNode methodNode : methodList){
                callMethod(methodNode, callerClassName);
            }

        } catch(Exception e){
            System.out.println("collect call: error: " + e);
        }
    }

    private void callMethod(MethodNode methodNode, String callerClassName){
        InsnList insnList = methodNode.instructions;
        //System.out.println("methodNode name: " + methodNode.name);
        //System.out.println("methodNode desc: " + methodNode.desc);
        String callerMethodName = methodNode.name + methodNode.desc;
        String callerFullName = callerClassName + "#" + callerMethodName;
        //System.out.println("callerFullName: " + callerFullName);
        this.classMethodDict.get(callerClassName).add(callerMethodName);

        ListIterator insnIter = insnList.iterator();
        while(insnIter.hasNext()){
            Object obj = insnIter.next();
            if(obj instanceof LineNumberNode){
                this.lineNo = ((LineNumberNode)obj).line;
            }
            else if(obj instanceof MethodInsnNode){
                MethodInsnNode methodInsnNode = (MethodInsnNode) obj;
                String calleeClassName = methodInsnNode.owner;
                String calleeMethodName = methodInsnNode.name + methodInsnNode.desc;
                String calleeFullName = calleeClassName.replace('/', '.') + "#" + calleeMethodName;
                // check if callee belongs to target project or not
                List<String> wordList = Arrays.asList(calleeClassName.split("/"));
                String calleePackageName = String.join(".", wordList.subList(0, (wordList.size()-1)));
                //System.out.println("calleePackageName: " + calleePackageName);

                if(this.packageSet.contains(calleePackageName)){
                    String callerInfo = callerFullName + ":" + this.lineNo;
                    this.callgraphDict.put(callerInfo, calleeFullName);
                    this.writer.writeRow(new String[]{callerInfo, calleeFullName});
                }
            }
        }


    }

    public static class MethodCallVisitor extends VoidVisitorAdapter<ParserWriter>{
        private static String startLine(Node node){
            if (node == null)
                return "-1";
            return Integer.toString(node.getRange().isPresent() ? node.getRange().get().startLine() : -1);
        }

        private static String endLine(Node node){
            if(node == null)
                return "-1";
            return Integer.toString(node.getRange().isPresent() ? node.getRange().get().endLine() : -1);
        }

        @Override
        public void visit(MethodCallExpr methodCallExpr, ParserWriter writer){
            //System.out.println("");
            String result[] = {startLine(methodCallExpr),
                    String.join("#", new String[]{methodCallExpr.getScope().get().toString(),
                            methodCallExpr.getName().toString()})};
            writer.writeRow(result);
            super.visit(methodCallExpr, writer);
        }

        @Override
        public void visit(final CompilationUnit n, ParserWriter writer) {
            //n.getImports().forEach(p -> p.accept(this, writer));
            //n.getModule().ifPresent(l -> l.accept(this, writer));
            //n.getPackageDeclaration().ifPresent(l -> l.accept(this, writer));
            //n.getTypes().forEach(p -> p.accept(this, writer));
            //n.getComment().ifPresent(l -> l.accept(this, writer));
            //n.getImports().forEach(p -> System.out.println("import: "+p.toString()));
            //n.getModule().ifPresent(l -> System.out.println("module: "+l.toString()));
            //n.getPackageDeclaration().ifPresent(l -> System.out.println("package: "+l.toString()));
            //n.getTypes().forEach(p -> System.out.println("type: "+p.toString()));
            //n.getComment().ifPresent(l -> System.out.println("comment: "+l.toString()));
            super.visit(n, writer);
        }

        @Override
        public void visit(final NodeList nodeList, ParserWriter writer){
            System.out.println("visit NodeList");
            int num = nodeList.size();
            for(int i=0; i!=num; i++)
                System.out.println(i+" : "+nodeList.get(i).toString());
            super.visit(nodeList, writer);
        }

        @Override
        public void visit(final AnnotationDeclaration annotationDeclaration, ParserWriter writer){
            System.out.println("visit annotationDeclaration");
            super.visit(annotationDeclaration, writer);
        }

        @Override
        public void visit(final ClassOrInterfaceDeclaration classOrInterfaceDeclaration,
                          ParserWriter writer){
            System.out.println("visit classOrInterface Declaration");
            System.out.println(classOrInterfaceDeclaration.getName());
//            classOrInterfaceDeclaration.getExtendedTypes().forEach(
//                    e -> System.out.println("extended: "+e.toString())
//            );
//            classOrInterfaceDeclaration.getImplementedTypes().forEach(
//                    i -> System.out.println("implemented: " + i.toString())
//            );
//            classOrInterfaceDeclaration.getTypeParameters().forEach(
//                    t -> System.out.println("type parameter: " + t.toString())
//            );
            super.visit(classOrInterfaceDeclaration, writer);
        }

        @Override
        public void visit(final EnumDeclaration enumDeclaration, ParserWriter writer){
            System.out.println("visit enumDeclaration");
            super.visit(enumDeclaration, writer);
        }


    }
}
