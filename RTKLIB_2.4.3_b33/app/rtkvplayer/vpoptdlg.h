//---------------------------------------------------------------------------

#ifndef vpoptdlgH
#define vpoptdlgH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <FMX.Controls.hpp>
#include <FMX.Forms.hpp>
#include <FMX.Controls.Presentation.hpp>
#include <FMX.StdCtrls.hpp>
#include <FMX.Types.hpp>
#include <FMX.Edit.hpp>
//---------------------------------------------------------------------------
class TVideoPlayerOptDialog : public TForm
{
__published:	// IDE �ŊǗ������R���|�[�l���g
	TButton *BtnOk;
	TButton *BtnCancel;
	TLabel *Label1;
	TLabel *Label2;
	TLabel *Label3;
	TEdit *EditMjpgRate;
	TEdit *EditSyncAddr;
	TEdit *EditSyncPort;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall BtnOkClick(TObject *Sender);
private:	// ���[�U�[�錾
public:		// ���[�U�[�錾
	__fastcall TVideoPlayerOptDialog(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TVideoPlayerOptDialog *VideoPlayerOptDialog;
//---------------------------------------------------------------------------
#endif
