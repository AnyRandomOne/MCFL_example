package com.sklcs.mainProject;

import java.io.File;
import java.util.ArrayList;

public class AllFileResolver extends AbstractResolver {
    public ArrayList<String> forCompare;
    private String suffix;

    public AllFileResolver(String basicPath, String suffix){
        super();
        this.forCompare = new ArrayList<>();
        this.suffix = suffix;
        this.findAllFiles(basicPath);
        //for(String debug: this.fileToAnalyze)
        //    System.out.println("find: " + debug);
    }

    private void findAllFiles(String basicPath){
        this.reachFile(basicPath);
        System.out.println("find " + forCompare.size() + " in all");
    }

    private void reachFile(String path){
        File fileNow = new File(path);
        if(!fileNow.exists()){
            System.out.println(path + "does not exist!");
            return;
        }
        //this is a file, instead of a director.
        if(!fileNow.isDirectory()){
            String fileName = fileNow.getName();
            String suffix = fileName.substring(fileName.lastIndexOf(".")+1);
            if(suffix.equals(this.suffix)){
                this.fileToAnalyze.add(path);
                String javaFileName = fileName.substring(0, fileName.lastIndexOf("."));
                //System.out.println(javaFileName);
                //for(String fileNameToCheck : this.forCompare){
                //    if(javaFileName.equals("package-info"))
                        //break;
                    //if(fileNameToCheck.equals(javaFileName)){
                        //System.out.println("twice: " + fileNameToCheck);
                    //}
                //}
                this.forCompare.add(javaFileName);
            }
            return;
        }
        String[] fileList= fileNow.list();
        if(fileList == null ||fileList.length == 0)
            return;
        for(String file: fileList){
            String wholeFile = path + '/' + file;
            this.reachFile(wholeFile);
        }
        //System.out.println("find " + fileList.length + "in all");
    }
}
