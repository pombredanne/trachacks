package mm.eclipse.trac.editors;

import mm.eclipse.trac.Log;
import mm.eclipse.trac.models.WikiPage;

import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResourceChangeEvent;
import org.eclipse.core.resources.IResourceChangeListener;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IEditorSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.part.FileEditorInput;
import org.eclipse.ui.part.MultiPageEditorPart;
import org.eclipse.ui.texteditor.ITextEditor;

/**
 * An example showing how to create a multi-page editor. This example has 3
 * pages:
 * <ul>
 * <li>page 0 contains a nested text editor.
 * <li>page 1 allows you to change the font used in page 2
 * <li>page 2 shows the words in page 0 in sorted order
 * </ul>
 */
public class WikiEditor extends MultiPageEditorPart implements
        IResourceChangeListener
{
    
    /** The text editor used in page 0. */
    private WikiSourceEditor editor;
    
    /** The text widget used in page 2. */
    private WikiPreview      wikiPreview;
    
    private Composite        previewFrame;
    
    /**
     * Creates a multi-page editor example.
     */
    public WikiEditor()
    {
        super();
        ResourcesPlugin.getWorkspace().addResourceChangeListener( this );
    }
    
    /**
     * Creates page 0 of the multi-page editor, which contains a text editor.
     */
    void createPageSource()
    {
        try
        {
            editor = new WikiSourceEditor();
            int index = addPage( editor, getEditorInput() );
            setPageText( index, "Source" );
        } catch ( PartInitException e )
        {
            ErrorDialog.openError( getSite().getShell(),
                                   "Error creating nested text editor", null, e
                                           .getStatus() );
        }
    }
    
    /**
     * Creates page 2 of the multi-page editor, which shows the sorted text.
     */
    void createPagePreview()
    {
        previewFrame = new Composite( getContainer(), SWT.NONE );
        FillLayout layout = new FillLayout();
        wikiPreview = new WikiPreview( previewFrame );
        previewFrame.setLayout( layout );
        
        int index = addPage( previewFrame );
        setPageText( index, "Preview" );
    }
    
    /**
     * Creates the pages of the multi-page editor.
     */
    protected void createPages()
    {
        createPageSource();
        createPagePreview();
    }
    
    /**
     * The <code>MultiPageEditorPart</code> implementation of this
     * <code>IWorkbenchPart</code> method disposes all nested editors.
     * Subclasses may extend.
     */
    public void dispose()
    {
        ResourcesPlugin.getWorkspace().removeResourceChangeListener( this );
        super.dispose();
    }
    
    /**
     * Saves the multi-page editor's document.
     */
    public void doSave( IProgressMonitor monitor )
    {
        Log.info( "Saving file." );
        getEditor( 0 ).doSave( monitor );
    }
    
    /**
     * Saves the multi-page editor's document as another file. Also updates the
     * text for page 0's tab, and updates this multi-page editor's input to
     * correspond to the nested editor's.
     */
    public void doSaveAs()
    {
        IEditorPart editor = getEditor( 0 );
        editor.doSaveAs();
        setPageText( 0, editor.getTitle() );
        setInput( editor.getEditorInput() );
    }
    
    /*
     * (non-Javadoc) Method declared on IEditorPart
     */
    public void gotoMarker( IMarker marker )
    {
        setActivePage( 0 );
        IDE.gotoMarker( getEditor( 0 ), marker );
    }
    
    /**
     * The <code>MultiPageEditorExample</code> implementation of this method
     * checks that the input is an instance of <code>IFileEditorInput</code>.
     */
    public void init( IEditorSite site, IEditorInput editorInput )
            throws PartInitException
    {
        super.init( site, editorInput );
        setPartName( editorInput.getName() );
        setTitleToolTip( editorInput.getToolTipText() );
    }
    
    /*
     * (non-Javadoc) Method declared on IEditorPart.
     */
    public boolean isSaveAsAllowed()
    {
        return false;
    }
    
    public ITextEditor getTextEditor()
    {
        return editor;
    }
    
    /**
     * Calculates the contents of page 2 when the it is activated.
     */
    protected void pageChange( int newPageIndex )
    {
        super.pageChange( newPageIndex );
        
        if ( newPageIndex == 1 )
        {
            if ( wikiPreview == null )
            {
                // wikiPreview = new WikiPreview( previewFrame );
            }
            
            String editorText = editor.getDocumentProvider()
                    .getDocument( editor.getEditorInput() ).get();
            WikiPage page = (WikiPage)((WikiEditorInput)editor.getEditorInput()).getWikiPage();
            wikiPreview.showContent( page, editorText );
            wikiPreview.setFocus();
        }
    }
    
    /**
     * Closes all project files on project close.
     */
    public void resourceChanged( final IResourceChangeEvent event )
    {
        if ( event.getType() == IResourceChangeEvent.PRE_CLOSE )
        {
            Display.getDefault().asyncExec( new Runnable() {
                public void run()
                {
                    IWorkbenchPage[] pages = getSite().getWorkbenchWindow()
                            .getPages();
                    for ( int i = 0; i < pages.length; i++ )
                    {
                        if ( ((FileEditorInput) editor.getEditorInput())
                                .getFile().getProject()
                                .equals( event.getResource() ) )
                        {
                            IEditorPart editorPart = pages[i]
                                    .findEditor( editor.getEditorInput() );
                            pages[i].closeEditor( editorPart, true );
                        }
                    }
                }
            } );
        }
    }
    
}
