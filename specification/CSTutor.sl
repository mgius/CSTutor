(* TODO: define a path *)
object Stats
	components: (Page, date:string, notes:string)*;
	description: (* A Stats is tied to a particular user, through the roster, and has a list of notable actions performed by said user, along with the datetime of the action, and any notes that are useful for later data crunching. *);
end Stats;

object Course
	components: p:Page* and r:Roster and privateClass:boolean and name:string and chatRoom:string and Stats and text:string*;
	operations: AddPage, RemovePage, SetPrivate, EditCourse;
	description: (* A course is a course. It contains zero or more pages, a course roster, a boolean determining whether or not the course is public or private, a string for the name of the course, a string for the chat room, a Stats object containing all of the course specific statistics, and a string containing a welcome text for the course *);
end Course; 

(* TODO: define AddPage, RemovePage, SetPrivate *)
operation AddPage
end AddPage;

operation RemovePage
end RemovePage;

operation SetPrivate
end SetPrivate;

object Page
	components: prevPage:Page and nextPage:Page and prereq:Page*;
	description: (* A Page has a link to the previous and next pages, as well as zero or more Page prerequisites.*); 
end Page;

object Lesson extends Page
	components: text:string* and code:string* and subtopic:Page*;
	operations: AddPage, RemovePage, EditLesson;
	description: (* A lesson is a specific type of Page. It contains zero or more text fields, zero or more code fields, and links to any subpages *);
end Lesson;

(* TODO: define a path *)
object Path
end Path;

object Quiz extends Page
	components: Question* and text:string* and title:string and Path and hidden:boolean;
	operations: AddQuestion, RemoveQuestion, EditQuiz, SubmitAnswers, CheckAnswers;
	description: (* A quiz is a specific type of Page. It contains zero or more Questions, a title string, zero or more text fields. It also contains a link to a Page being required as a prerequisite and a boolean for visibility.*);
end Quiz;

object Question
	components: text:string* and question:string;
	description: (* A Question is question. It contains a string for the prompt, and a string for the title *);
end Question;

object MultipleChoiceQuestion extends Question
	components: Answer*;
	description: (* A multiple choice question is a specific type of question. It contains a list of possible Answers. *);
end MultipleChoiceQuestion;

object Answer
	components: answer:string and correct:boolean;
	description: (* A answer is a possible answer for a multiple choice question. It contains a string for the answer and a boolean determining whether or not the answer is correct.*);
end Answer;

object CodeQuestion extends Question
	components: code:string and output:string;
	operations: compareOutput;
	description: (* A code question is a specific type of question. It allows for code to be entered which is then ran and the output is compared against predefined output. It contains a string for their code, and a string for the correct output *);
end CodeQuestion;

operation compareOutput
	inputs: userCode:string and correctOutput:string;
	outputs: correct: boolean and output:string;
	description: (*This operation takes in a users code snippet, runs it, and compares the output. It returns a boolean whether the output matched, as well as the correct output.*);
end compareOutput;

object Roster
	components: (User, Permissions, Stats)*;
	operations: addUser, deleteUser, editPermissions;
	description: (* A roster keeps track of the permissions and statistics for all associated users. *);
end Roster;

operation editPermissions
	inputs: user:User and modifiedPermissions:Permissions;
	outputs: newPermissions:Permissions;
	description: (*This operation takes a user and a set of modified permissions, replaces the old permissions, and returns an updated permissions*);
end editPermissions;

object User
	components: isInstructor:boolean and userName:string and password:string and enrolled:Course* and email:string;
	operations: editProfile;
	description: (* A user contains a boolean determining whether or not the user has instructor permissions, a string for the username, a string for the password, and a list of Courses that the user is enrolled in. Additionally, a user may provide an email address. *);
end User;

operation editProfile
	inputs: currentProfile:User and modifiedProfile:User;
	outputs: newProfile:User;
	description: (*This operation takes a users profile and any modifications and merges them together, returning an updated profile*);
end editProfile;

object Permissions
	components: view:boolean and edit:boolean and stats:boolean and manage:boolean;
	description: (* Permissions are a set of booleans that map the permissions for users. The view permission allows the user to view the course material. The edit permission allows the user to edit the course material. The stats permission allows the user to view class-wide statistics and roster. The manage permission allows the user to modify the roster and all associated permissions *);
end Permissions;


(* TODO: define createCourse, removeCourse, createLesson, removeLesson, removePage *)

operation createCourse
	inputs: name:string and private:boolean and instructor:User; 
	outputs: newCourse:Course;
	description: (* A new course is created when an Instructor user clicks on the Create Class button.  createCourse takes in a string for the class name, a boolean that specifies if the class is privately or publicly available and a User which is the creator of the class.  createCourse returns a new Course in which the User passed in as the intructor has Manage permissions *);
end createCourse;

operation removeCourse
	inputs: toRemove:Course;
	outputs: success:boolean;
	description: (* A course is removed from CSTutor when the delete button is hit for the Course.  removeCourse takes in a Course to be removed and returns a boolean saying if the delete succeeded or not *);
end removeCourse;

operation createLesson
	inputs: name:string and course:Course;
	outputs: newLesson:Lesson;
	description; (* A lesson is created when an user with manage permissions for a Course clicks Submit on the Add Lesson page.  createLesson takes in a string for the name and a Course in which the lesson will be contained. createLesson returns the new created Lesson *)
end createLesson;

operation removePage
	inputs: toRemove:Page;
	outputs: success:boolean;
	description: (* A page is removed from CSTutor when the delete button is hit for the Course.  removeCourse takes in a Page, either a Lesson or Quiz, to be removed and returns a boolean saying if the delete succeeded or not *);
end removeLesson;

operation createQuiz
	inputs: oldCourse:Course and newQuiz:Quiz;
	outputs: newCourse:Course;
	description: (* Takes a course as well as the form submitted containing the new quiz and creates a new Course page containing the quiz *);
end createQuiz;

operation deleteQuiz
	inputs: quiz:Quiz and course:Course;
	outputs: newCourse:Course;
	description: (* Takes a course and a specified quiz and deletes the quiz from the course. It also deletes any corresponding statistics *);
end deleteQuiz;

operation editQuiz
	inputs: oldQuiz:Quiz and modifiedQuiz:Quiz;
	outputs: newQuiz:Quiz;
	description: (* Takes an old Quiz, the Quiz containing the changes, and merges the changes in the modified quiz into the old Quiz *);
end editQuiz;

operation addQuestion
	inputs: quiz:Quiz and q:Question;
	outputs: newQuiz:Quiz;
	description: (* Takes the quiz being worked on and the question being added, and adds the question to the quiz *);
end addQuestion;

operation removeQuestion
	inputs: quiz:Quiz and q:Question;
	outputs: newQuiz:Quiz;
	description: (* Takes the quiz being worked on and the question being removed, and removes the question from the quiz *);
end removeQuestion;

operation clearStatistics
	inputs: stats:Stats;
	outputs: freshStats:Stats;
	description: (* Clear a set of statistics. *);
end clearStatistics;

operation displayStats
	inputs: Stats;
	outputs: string;
	description:  (*Takes in a Stats and returns the content to display *);
end displayStats;

operation getStats
	inputs: roster:Roster;
	outputs: stats:Stats;
	description: (* Get the statistics for a class from the roster *);
end getStats;

operation getNextPage
	inputs: Page;
	outputs: Page;
	description: (*Takes in a Page, and returns the next logical page.*);
end getNextPage;

operation getPrevPage
	inputs: Page;
	outputs: Page;
	description: (*Takes in a Page, and returns the previous logical page.*);
end getPrevPage;

operation displayPage
	inputs: Page;
	outputs: string;
	description:  (*Takes in a page and returns the content to display *);
end displayPage;

operation movePage
	inputs: Page and Page;
	outputs: boolean;
	description: (*Takes in two pages, the page to move and the page to 
	              place the moved page after, and moves the first page to be
	              the "next" of the second Page.  Returns boolean indicating 
	              success *);
end movePage;

operation login
	inputs: username:string, password:string, database:string;
	description: (* Takes in username and password then checks server to see if there is a
						match. If so then it grants access *);
end login;
	
operation logout
	inputs: userdata:string, database:string;
	description: (* saves all user data to the server *);
end logout;

operation addUser
	inputs: name:string and roster:Roster;
	outputs: updatedRoster:Roster;
	description: (* addUser adds the given string name into the Roster and produces an updated Roster. *);
end addUser;

operation removeUser
	inputs: name:string* and roster:Roster;
	outputs: updatedRoster:Roster;
	description: (* removeUser removes the inputed string names from the roster and produces an updated Roster. *);
end removeUser;

object PermissionSet
	components: name:string and edit:boolean and manage:boolean and states:boolean;
end PermissionSet;

operation setUserPermissions
	inputs: PermissionSet*;
	outputs: updatedRoster:Roster;
	description: (* setUserPermissions will take in a list of tuples consisting of a string name, boolean edit, boolean manage, and boolean states and will produce an updated Roster with the new user permissions. *);
end setUserPermissions;

operation updateRoster
	inputs: roster:Roster;
	outputs: updated:Roster;
	description: (* updateRoster will take in a roster and make the changes to a roster final. *);
end updateRoster;
